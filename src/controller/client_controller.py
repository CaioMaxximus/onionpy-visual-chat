# import queue
import asyncio
import threading
from .basic_async_controller import BasicAsyncController
from data_base import db_service_manager

# 
# Temporary

# RETRYABLE_ERRORS = (TimeoutError , ConnectionError , ConnectionAbortedError)

class ClientController(BasicAsyncController):


    """
        This class defines a controller for the client UI, working as Bridge/Dispatcher 
        between the UI layer and the connection layer

        Attributes
        ----------


        Methods
        -------
        The methods that have a '_' underscore at the begining version,are just the public version 
        of their counter part, using the queue to schedule theirs private selfs.

        run(host , port,gui_root ,callback )
            Creates a new Thread and defines a event loop for the controller lifecycle
        _start_event_loop()
            Start the event loop and iniate all the asynchronous queue
        _start_client
            Start the connection with a onion server
        _close_connection:
            Close the connection with the onion server
        _close_controller
            Shutdowns the controller event loop, closing all the connections in the process

    """

    def __init__(self,
                 service,notification_bus
                 ) -> None:
        super().__init__(service,notification_bus)
        self.connected = False

    def run(self, host: str, port: int, gui_root , callback) -> None:


        """
            Start point for the Thread, after the start, the lifecyle of the controller is 
            detached from the tkinter event loop.

            Parameters
            ----------
            host : str
                onion server hostname
            port : int
                onion server connection port
            gui_root: Tkinter
                the tkinter application root, it allows to schedule callback functions to 
                be executed by the UI layer
            callback: <funciton>
                executed after the asyncio event loop is defined

        """
        
        if not self.running:
            self.gui_loop = gui_root
            # self.HOST = host
            # self.PORT = port
            self.running = True
            thread = threading.Thread(
                target = self._start_event_loop, 
                args=(callback ,host , port  ) ,daemon=True)
            thread.start()
    
    ## This function can be moved for the superclass
    def _start_event_loop(self, callback ,host , port):

        """
            Instanciate the asynchronous queues inside the event loop and create the main task

            Parameters
            ---------
            callback : <function>
                function to be executed by the tkinter event loop after the controller is active
        """
      
        async def start():
            # self.message_queue = asyncio.Queue()
            # self.notification_queue = asyncio.Queue()
            self.function_queue = asyncio.Queue()  
            self.notification_bus.start()
     
            self.my_loop = asyncio.get_running_loop()
            await self.service.start(host , port)

            self.gui_loop.after(100,callback)
            self.running =  True
            # await self.function_queue.put((self._start_connection_control, () , None))
            self.main_routine = asyncio.create_task(self.dispatcher())

            await self.main_routine
            
        try:
            asyncio.run(start())
        except asyncio.CancelledError:
            pass


    def close_controller(self):
       self.my_loop.call_soon_threadsafe( # type: ignore
           lambda : asyncio.create_task(self._close_controller())  # type: ignore
       )
    
    async def _close_controller(self):
        
        try:
            await self.service._close_connection()
        except ConnectionError: 
            pass 
        finally:
            await self.stop_routines()

    def start_client(self,callback):
        self._enqueue(self.service._start_client ,callback= callback)
    
    def close_connection(self, callback):
        self._enqueue(self.service._close_connection,(),callback)
    
   