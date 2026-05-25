import asyncio
from typing import Any, Callable, Optional, Tuple
from src.models import Notification , NotificationType
from abc import ABC

#Temporary location
RETRYABLE_ERRORS = (TimeoutError , ConnectionError , ConnectionAbortedError)


class BasicAsyncController(ABC):

    """
        This class acts as a asynchronous controller,a background thread
        with his own asyncio event loop.

        It works as a bridge  between the UI and the network layer and also as a event
        dispacther, synchronizing the events wit h a function queue and data queues, 
        executing the callbacks and handling the exceptions.

        Responsibilities:
        - Dispatch async operations with retry logic
        - Forward messages and notifications from the connection layer
        - Execute UI callbacks safely via the GUI event loop

        Methods
        -------
        dispatcher_executer(func : Callable ,args , callback : Callable)
            core function to control the dispatcher of tasks comming from the UI layer,
            executing  callbacks, handle erros and the retryable operations
        dispatcher()
            auxiliar functions to dispatcher_executer, colects the function in the queue
            and creates the asynchronous tasks for each one, the functions were separeted
            to improve testability

    """

    def __init__(self, service,notification_bus):
        self.service = service
        self.notification_bus = notification_bus
        self.function_queue : Optional[asyncio.Queue] 

        self.HOST = None
        self.PORT = None

        self.running =  False
        self.retry_sleep_time = 0.8

        self.max_attempts_retry = 2
        self.main_routine: Optional[asyncio.Task] 
        self.all_running_tasks: dict[str, asyncio.Task] = {}
        self.my_loop: Optional[asyncio.AbstractEventLoop]
        self.gui_loop: Optional[Any]

    async def dispatcher_executer(self,func : Callable ,args , callback : Callable):
        """Asynchronously execute a callable with retry logic and callback handling.
        This coroutine repeatedly attempts to call the provided async callable until it succeeds, 
        the maximum number of retry attempts is reached, or the controller is stopped 
        (self.running becomes False). It converts exceptions into notification
        messages posted to self.notification_queue and invokes a provided callback on a successful
        result.

        Parameters
        ----------
        func : Callable
            Asynchronous callable to execute. It will be awaited as await func(*args).
        args : Sequence
            Sequence (e.g., tuple or list) of positional arguments to unpack into func.
            Note: keyword arguments are not supported by this dispatcher (only *args).
        callback : Callable
            Callable to be invoked with the successful result. The callback is executed
            via self._execute_callback(res, callback=callback).

        Behavior and side effects
        -------------------------
        - The dispatcher loops while self.running is True.
        - It will attempt to call func up to self.max_attempts_retry times.
        - If an exception that matches RETRYABLE_ERRORS is raised, a WARNING
          Notification containing the error message is put into self.notification_queue and the 
          dispatcher will retry after a backoff period (self.retry_sleep_time multiplied by 
          the attempt number).
        - If a non-retryable Exception is raised, an ERROR Notification is enqueued and the retry
          loop is aborted (the attempt counter is set to the max, causing an
          exit).
        - On successful execution (no exception), the result is passed to the provided
          callback through self._execute_callback and the dispatcher stops retrying.
        - If the maximum number of attempts is reached without success, an INFO Notification
          indicating the abort is enqueued and the dispatcher stops.
        - The method does not re-raise handled exceptions; instead it reports them via
          notifications. It returns None.

        Notes
        -----
        - This coroutine assumes:
          - self.notification_queue is an asyncio-compatible queue with a put method.
          - Notification and NotificationType classes/enums are available and used to
            represent messages.
          - self.max_attempts_retry and self.retry_sleep_time are configured numeric
            attributes on the instance.
          - self._execute_callback is responsible for invoking the callback safely.
        """

        attempt = 0
        # print(f" ATTENTION !! {func.__name__}")
        while self.running:
            if attempt < self.max_attempts_retry:
                if attempt > 0:
                    await asyncio.sleep(self.retry_sleep_time * attempt)
                try :
                    res = await asyncio.wait_for(func(*args),25.0)
                except RETRYABLE_ERRORS as e:
                    await self.notification_bus.send(
                        Notification(NotificationType.WARNING, f"{str(e)}")
                    )
                    attempt +=1
                except asyncio.TimeoutError:
                    # await self.notification_bus.send(
                    #     Notification(NotificationType.ERROR, f"Timeout executing {func.__name__}, action takes too long")
                    # ) 
                    attempt =  self.max_attempts_retry
                    pass
                    # raise e ## just for test
                except Exception as e:
                    await self.notification_bus.send(
                        Notification(NotificationType.ERROR, f"Error executing {func.__name__}: {str(e)}")
                    ) 
                    attempt =  self.max_attempts_retry
                    # raise e ## just for test

                else:
                    self._execute_callback( res , callback = callback)
                    break
            else:
                await self.notification_bus.send(
                    Notification(NotificationType.INFO ,
                                                f"Aborting execution of {func.__name__}:")
                )
                break


    async def dispatcher(self) -> None :
        """
        Asynchronously dispatches work items from an internal queue by scheduling executor tasks.
        This coroutine runs while self.running is truthy. It continuously awaits an item
        from self.function_queue (expected to be an asyncio.Queue) and expects each item to be a
        3-tuple of (func, args, callback). For each retrieved item it creates a background
        task that calls self.dispatcher_executer(func, args, callback) via asyncio.create_task,
        allowing the executor to run concurrently without blocking the dispatcher loop.

        Behavior and expectations:
        - Yields control while awaiting self.function_queue.get(), so other tasks can run.
        - Does not await the created tasks; exceptions raised in dispatcher_executer will surface
            on the created Task unless handled inside the executor.
        - The dispatcher is long-running; to stop it, set self.running = False or cancel the
            Task running this coroutine.
        - Assumes the instance provides:
                - self.function_queue: an asyncio.Queue producing (func, args, callback) tuples
                - self.dispatcher_executer: a coroutine/function that handles execution of each item

        Returns:
                None
        """
        try:
            ## nedd to keep track of this tasks later
            while self.running:
                func, args ,  callback = await self.function_queue.get()
                new_task = asyncio.create_task((self.dispatcher_executer(func , args ,  callback)))
        except asyncio.CancelledError:
            pass

    def _execute_callback(self,*args,callback = None):
        if callback is not None:
            self.gui_loop.after(10,callback,*args)

    
    def _enqueue(self, func : Callable, *args, callback=None):
        try:
            self.my_loop.call_soon_threadsafe(self.function_queue.put_nowait, (func, args, callback))
        except Exception as e:
            raise e
    

    async def stop_routines(self) -> None:
   
    ## need to prepare the enviroment for proper closing
        if self.running:
            self.running = False

            tasks: list[asyncio.Task] = []

            tasks = self.all_running_tasks.values()

            for t in tasks:
                try:
                    await t.cancel()
                except asyncio.CancelledError:
                    pass
                except Exception:
                    pass

            q = self.function_queue
            if q is not None:
                try:
                    while True:
                        q.get_nowait()
                except asyncio.QueueEmpty:
                    pass
            
            try:
                await self.main_routine.cancel()
            except asyncio.CancelledError:
                pass
            except Exception:
                pass
    
    def send_message_to_web(self, message: str, callback) -> None:
        self._enqueue( self._send_message_to_web , message, callback = callback)

    async def _send_message_to_web(self, message):
        await self.service.send_message(message)

    def get_web_message(self, callback) -> None:

        self._enqueue(self._get_web_message,callback= callback)


    def get_notification(self, callback) -> None:
        self._enqueue(self._get_notification, callback= callback)

    async def _get_notification(self) :
        return await self.notification_bus.consume()

    async def _get_web_message(self):
        msg = await self.service.get_message()
        return msg
    
    
