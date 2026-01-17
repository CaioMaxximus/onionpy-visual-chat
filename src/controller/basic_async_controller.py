import asyncio
from typing import Any, Callable, Optional, Tuple
from models.notification import Notification , NotificationType

#Temporary location
RETRYABLE_ERRORS = (TimeoutError , ConnectionError , ConnectionAbortedError)


class BasicAsyncController():

    def __init__(self, connection):
        self.connection = connection


        self.message_queue : Optional[asyncio.Queue] 
        self.notification_queue : Optional[asyncio.Queue] 
        self.function_queue : Optional[asyncio.Queue] 

        self.HOST = None
        self.PORT = None

        self.running =  False

        self.max_attempts_retry = 2
        self.notification_routine: Optional[asyncio.Task]
        self.message_routine: Optional[asyncio.Task] 
        self.main_routine: Optional[asyncio.Task] 
        # Python 3.9+
        self.all_running_tasks: dict[str, asyncio.Task] = {}

        self.my_loop: Optional[asyncio.AbstractEventLoop]
        self.gui_loop: Optional[Any]

    async def dispatcher_executer(self,func : Callable ,args , callback : Callable):
                        attempt = 0
                        # print(f" ATTENTION !! {func.__name__}")
                        while self.running:
                            if attempt < self.max_attempts_retry:
                                try :
                                    res = await func(*args)
                                    print("a funcao ja executei!")
                                    print(func.__name__)
                                except RETRYABLE_ERRORS as e:
                                    await self.notification_queue.put(
                                        Notification(NotificationType.WARNING, f"{str(e)}")
                                    )
                                    attempt +=1
                                    # raise e ## just for test
                                except Exception as e:
                                    await self.notification_queue.put(
                                        Notification(NotificationType.ERROR, f"Error executing {func.__name__}: {str(e)}")
                                    )
                                    attempt =  self.max_attempts_retry
                                    # raise e ## just for test

                                else:
                                    self._execute_callback( res , callback = callback)
                                    break
                            else:
                                await self.notification_queue.put(
                                    Notification(NotificationType.INFO ,
                                                                f"Aborting execution of {func.__name__}:")
                                )
                                break


    async def dispatcher(self) -> None :
        
        while self.running:
            func, args ,  callback = await self.function_queue.get()
            new_task = asyncio.create_task((self.dispatcher_executer(func , args ,  callback)))
    
    def _execute_callback(self,*args,callback = None):
        if callback is not None:
            self.gui_loop.after(10,callback,*args)

    
    def _enqueue(self, func : Callable, *args, callback=None):
        try:
            self.my_loop.call_soon_threadsafe(self.function_queue.put_nowait, (func, args, callback))
        except Exception as e:
            raise e

    async def _get_notification_on_connection_routine(self):
        while self.running:
            try :
                notification = await self.connection.get_notification_in_queue()
                await self.notification_queue.put(notification)
            except asyncio.CancelledError:
                pass
    
        
    async def start_routines(self):
        self.notification_routine = asyncio.create_task(
            self._get_notification_on_connection_routine()
        )
        self.message_routine = asyncio.create_task(
            self._get_messages_on_connection_routine()
        )
    

    async def stop_routines(self) -> None:
   
        self.running = False

        tasks: list[asyncio.Task] = []
        for routine in (self.notification_routine, self.message_routine):
            routine.cancel()
            print("mandei encerra a primeira rotina do controller")
            try:
                await routine
            except asyncio.CancelledError:
                pass
            except Exception:
                pass
        print("encerrei duas rotinas!")

        tasks = self.all_running_tasks.values()
        for t in tasks:
            if not t.done():
                t.cancel()
        for t in tasks:
            try:
                await t
            except asyncio.CancelledError:
                pass
            except Exception:
                pass
            print("encerrei as tasks presentes!")


        for q in (self.message_queue, self.notification_queue, self.function_queue):
            if q is None:
                continue
            try:
                while True:
                    q.get_nowait()
            except asyncio.QueueEmpty:
                pass
        print("linpei as fi]las")

        self.main_routine.cancel()
        try:
            await self.main_routine
        except asyncio.CancelledError:
            pass
        except Exception:
            pass

        # self.message_queue = None
        # self.notification_queue = None
        # self.function_queue = None
        # print("encerrei as rotinas do controller")
    

        
    async def _get_messages_on_connection_routine(self):
        while self.running:
            try :
                msg = await self.connection.get_message_in_queue()
                await self.message_queue.put(msg)
            except asyncio.CancelledError:
                pass

    
    def send_message_to_web(self, message: str, callback) -> None:
        self._enqueue( self._send_message_to_web , message, callback = callback)

    async def _send_message_to_web(self, message):
        await self.connection.send_message(message)

    def get_web_message(self, callback) -> None:
        self._enqueue(self._get_web_message,callback= callback)


    def get_notification(self, callback) -> None:
        self._enqueue(self._get_notification, callback= callback)

    async def _get_notification(self) :
        return await self.notification_queue.get()

    async def _get_web_message(self):
        return await self.message_queue.get()
    
    
