import queue
import asyncio
from models.notification import Notification , NotificationType
import threading

# 
# Temporary

RETRYABLE_ERRORS = (TimeoutError , ConnectionError , ConnectionAbortedError)

class ClientController:

    def __init__(self,
                 connection,
                 ) -> None:

        self.connection = connection
        self.data_queue = None
        self.notification_queue = None
        self.function_queue = None
        self.HOST = None
        self.PORT = None
        self.running =  False
        self.max_attempts_retry = 1
        self.notification_routine = None
        self.message_routine = None
        self.main_task = None
        self.loop = None
        self.all_running_tasks = []


    def run(self, host: str, port: int, gui_root , callback) -> None:
        
        if not self.running:
            self.gui_loop = gui_root
            self.HOST = host
            self.PORT = port
            self.running = True
            thread = threading.Thread(
                target = self.start_event_loop, 
                args=(callback , ) ,daemon=True)
            thread.start()
    
    def start_event_loop(self, callback):
      
        async def start():
            self.data_queue = asyncio.Queue()
            self.notification_queue = asyncio.Queue()
            self.function_queue = asyncio.Queue()       
            self.loop = asyncio.get_running_loop()
            # await self.function_queue.put((self._start_connection_control, () , None))
            self.main_task = asyncio.create_task(self.check_function_queue())
            self.gui_loop.after(100,callback)

            await self.main_task
            
        asyncio.run(start())
            

    async def check_function_queue(self):
        async def wrapped(func ,args , callback):
            attempt = 0
            print(f" ATTENTION !! {func.__name__}")
            while self.running:
                if attempt < self.max_attempts_retry:
                    try :
                        res = await func(*args)
                    except RETRYABLE_ERRORS as e:
                        await self.notification_queue.put(
                            Notification(NotificationType.WARNING, f"{str(e)}")
                        )
                        attempt +=1
                        raise e
                    except Exception as e:
                        await self.notification_queue.put(
                            Notification(NotificationType.ERROR, f"Error executing {func.__name__}: {str(e)}")
                        )
                        attempt =  self.max_attempts_retry
                        raise e

                    else:
                        self._execute_callback( res , callback = callback)
                        break
                else:
                    await self.notification_queue.put(
                        Notification(NotificationType.INFO ,
                                                       f"Aborting execution of {func.__name__}:")
                    )
                    break

        while True:
            func, args ,  callback = await self.function_queue.get()
            new_task = asyncio.create_task((wrapped(func , args ,  callback)))
            # self.all_running_tasks.append(new_task) # idéia a desenvolver
            

    def _execute_callback(self,*args,callback = None):
        if callback is not None:
            self.gui_loop.after(10,callback,*args)

    def start_client(self,callback):
        self._enqueue(self._start_client ,callback= callback)

    async def _start_client(self) -> None:

        await self.connection.run(self.HOST, self.PORT)
        await self.function_queue.put((self._get_notification_on_connection_routine, (),None))
        await self.function_queue.put((self._get_messages_on_connection_routine, (),None))

        
        # self.notification_routine = asyncio.create_task(
        #     self._get_notification_on_connection_routine())
        # self.message_routine = asyncio.create_task(
        #     self._get_messages_on_connection_routine())

    def _enqueue(self, func, *args, callback=None):
        try:
            self.loop.call_soon_threadsafe(self.function_queue.put_nowait, (func, args, callback))
        except Exception as e:
            raise e


    def send_message_to_web(self, message: str, callback) -> None:
        self._enqueue( self._send_message_to_web , message, callback = callback)

    async def _send_message_to_web(self, message):
        await self.connection.send_message(message)

    # def start_connection(self, callback) -> None:
    #     self._enqueue(self._start_connection_control, callback= callback)


    def get_web_message(self, callback) -> None:
        self._enqueue(self._get_web_message,callback= callback)


    def get_notification(self, callback) -> None:
        self._enqueue(self._get_notification, callback= callback)

    async def _get_notification(self) :
        return await self.notification_queue.get()

    async def _get_web_message(self):
        return await self.data_queue.get()
    
    # def _insert_web_message_in_queue(self, message: str) -> None:
    #     self.data_queue.put(message)
    

    # def _insert_notification_in_queue(self, notification: str) -> None:
    #     self.notification_queue.put( notification)
        
    async def _get_notification_on_connection_routine(self):
        try :
            notfication = await self.connection.get_notification_in_queue()
            await self.notification_queue.put(notfication)
            await self.function_queue.put((self._get_notification_on_connection_routine, () , None))
        except asyncio.CancelledError:
            print("deu erro na coleta da notificacao")
            raise
        
    async def _get_messages_on_connection_routine(self):
        # while True:
        try :
            msg = await self.connection.get_message_in_queue()
            await self.data_queue.put(msg)
            await self.function_queue.put((self._get_messages_on_connection_routine, (),None))
        except asyncio.CancelledError:
            print("deu erro na coleta da messagem")
            raise