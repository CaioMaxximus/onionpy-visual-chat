# import queue
import asyncio
# from models.notification import Notification , NotificationType
import threading
from .basic_async_controller import BasicAsyncController

# 
# Temporary

# RETRYABLE_ERRORS = (TimeoutError , ConnectionError , ConnectionAbortedError)

class ClientController(BasicAsyncController):

    def __init__(self,
                 connection,
                 ) -> None:
        super().__init__(connection)
        self.connected = False

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
            self.message_queue = asyncio.Queue()
            self.notification_queue = asyncio.Queue()
            self.function_queue = asyncio.Queue()       
            self.my_loop = asyncio.get_running_loop()
            self.running =  True
            # await self.function_queue.put((self._start_connection_control, () , None))
            self.main_routine = asyncio.create_task(self.dispatcher())
            self.gui_loop.after(100,callback)

            await self.main_routine
            
        try:
            asyncio.run(start())
        except asyncio.CancelledError:
            pass
        print("==========")
        print("este controle foi encerrado com sucesso a thread acaba de moerrer filhote !!!")


    def close_controller(self):
       self.my_loop.call_soon_threadsafe( # type: ignore
           lambda : asyncio.create_task(self._close_controller())  # type: ignore
       )
    
    def close_connection(self, callback):
        self._enqueue(self._close_connection,(),callback)
    
    async def _close_connection(self):
        if self.connected:
            await self.connection.close_connection()
            self.connected = False
        else:
            raise ConnectionError("The connection is already closed!")
    
    async def _close_controller(self):
        try:
            await self._close_connection()
        except ConnectionError:
            pass 
        finally:
            await self.stop_routines()

    def start_client(self,callback):
        self._enqueue(self._start_client ,callback= callback)

    async def _start_client(self) -> None:

        await self.connection.run(self.HOST, self.PORT)
        self.connected = True

        await self.start_routines()
   