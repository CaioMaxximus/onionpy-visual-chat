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

        self.client_connection = connection
        self.data_queue = asyncio.Queue()
        self.notification_queue = asyncio.Queue()
        self.function_queue = asyncio.Queue()
        self.HOST = None
        self.PORT = None
        self.running =  False
        self.max_attempts_retry = 2
        self.notification_routine = None
        self.message_routine = None



    def run(self, host: str, port: int, gui_root) -> None:
        
        
        if not self.running:
            self.gui_loop = gui_root
            self.HOST = host
            self.PORT = port
            self.running = True
            thread = threading.Thread(target=lambda : (self.start_event_loop), daemon=True)
            thread.start()
    
    def start_event_loop(self):
        
        async def start():
            self.function_queue.put(self._start_connection_control, () , None)
            self.main_task =  await self.check_function_queue()
            
        asyncio.run(start)
            

    async def check_function_queue(self):
        async def wrapped(func ,args , callback):
            attempt = 0
            while self.running:
                if attempt < self.max_attempts_retry:
                    try :
                        res = await func(*args)
                    except RETRYABLE_ERRORS as e:
                        await self.notification_queue.put(
                            Notification(NotificationType.WARNING, f"{str(e)}")
                        )
                        attempt +=1
                        pass 
                    except Exception as e:
                        await self.notification_queue.put(
                            Notification(NotificationType.ERROR, f"Error executing {func.__name__}: {str(e)}")
                        )
                        attempt =  self.max_attempts_retry
                    else:
                        self._execute_callback(callback , res)
                else:
                    await self.notification_queue.put(NotificationType.INFO ,
                                                       f"Aborting execution of {func.__name__}:")
                    break
                

        while True:
            func, args ,  callback = await self.function_queue.get()
            asyncio.create_task((wrapped(func , args ,  callback)))
            

    def _execute_callback(self,callback , *args):
        if callback is not None:
            self.gui_loop.after(10,callback,*args)


    async def _start_connection_control(self) -> None:
        
        self.notification_routine = asyncio.create_task(
            self._get_notification_on_connection_routine())
        await self.client_connection.async_server(self.HOST, self.PORT)
        self.message_routine = asyncio.create_task(
            self._get_messages_on_connection_routine())

    def _enqueue(self, func, args=(), callback=None):
        try:
            self.function_queue.put_nowait((func, args, callback))
        except Exception:
            pass


    def send_message_to_web(self, message: str, callback: callable = None) -> None:
        self._enqueue(self.client_connection.add_message_to_send, (message,), callback)


    def start_connection(self, callback: callable = None) -> None:
        self._enqueue(self._start_connection_control, (), callback)


    def get_web_message(self, callback: callable = None) -> None:
        self._enqueue(self._get_web_message, (), callback)


    def get_notification(self, callback: callable = None) -> None:
        self._enqueue(self._get_notification, (), callback)

    async def _get_notification(self) :
        return await self.notification_queue.get()

    async def _get_web_message(self):
        return await self.data_queue.get()
    
    def _insert_web_message_in_queue(self, message: str) -> None:
        self.data_queue.put(message)
    

    # def _insert_notification_in_queue(self, notification: str) -> None:
    #     self.notification_queue.put( notification)
        
    async def _get_notification_on_connection_routine(self):
        while True:
            try :
                await self.connection.get_notification_in_queue()
            except asyncio.CancelledError():
                pass
            
    async def _get_messages_on_connection_routine(self):
        while True:
            try :
                await self.connection.get_message_in_queue()
            except asyncio.CancelledError():
                pass