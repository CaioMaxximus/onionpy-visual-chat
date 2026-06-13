import queue
import asyncio
import threading
from src.connection import TorServiceManager
from data_base import repository
import random
import socket
from .base_async_controller import BaseAsyncController
# from threading import Thread
from src.error.special_errors import ConnetionClosedError
from models import OnionServer



class ServerController(BaseAsyncController):

    """
        This class defines a controller for the server UI, working as Bridge/Dispatcher 
        between the UI layer and the connection layer

        Attributes
        ----------
        server_name: str
            local name for the server

        Methods
        -------
        The methods that have a '_' underscore at the begining version,are just the public version 
        of their counter part, using the queue to schedule theirs private selfs.

        run()
            Creates a new Thread and defines a event loop for the controller lifecycle
        start_event_loop()
            Start the event loop and iniate all the asynchronous queue
        _create_server(rollback_operations, name)
            Creates a new server with a valid -name-
        _start_server(self,name)
            Starts a existing server  
        _close_server
            Stops the onion service and the local asynchronous server
        _close_controller
            Shutdowns the controller event loop, closing all the connections in the process

    """

    def __init__(self, connection , server_name, notification_bus):
        super().__init__(connection,notification_bus)
        self.server_name = server_name


    def run(self, gui_root , callback) -> None:

        """
            Start point for the Thread, after the start, the lifecyle of the controller is 
            detached from the tkinter event loop.

            Parameters
            ----------
            gui_root: Tkinter
                the tkinter application root, it allows to schedule callback functions to 
                be executed by the UI layer
            callback: <funciton>
                executed after the asyncio event loop is defined

        """
        
        if not self.running:
            self.gui_loop = gui_root
            self.running = True
            thread = threading.Thread(
                target=self.start_event_loop,
                args=(callback,),   
                daemon=True)

            thread.start()
            
     ## This function can be moved for the superclass partially
    def start_event_loop(self ,callback):

        """
            Instanciate the asynchronous queues inside the event loop,
            initate the data base and create the main task

            Parameters
            ---------
            callback : <function>
                function to be executed by the tkinter event loop after the controller is active
        """
    
        async def start():
            # self.message_queue = asyncio.Queue()
            # self.notification_queue = asyncio.Queue()
            self.notification_bus.start()
            self.function_queue = asyncio.Queue()
            await self.service.start()
            self.my_loop = asyncio.get_running_loop()
            await repository.create_tables()
            self.running =  True
            self.gui_loop.after(100,callback)
            self.main_routine = asyncio.create_task(self.dispatcher())
            await self.main_routine
        try:
            asyncio.run(start())
        except asyncio.CancelledError:
            pass

    def start_server(self, name , callback):
        self._enqueue(self.service._start_server, name ,callback = callback)
    
    def create_server(self ,name , callback):
        self._enqueue(self.service._create_server , name, callback = callback)

    def close_server(self ,callback):
        self._enqueue(func=self._close_server,callback=callback)

    def close_controller(self):
        self.my_loop.call_soon_threadsafe( # type: ignore
            lambda: asyncio.create_task(self._close_controller())  # type: ignore
        )
    
    async def _close_server(self):
        await self.service.close_server()

    
    async def _close_controller(self):

        try:  
            await self._close_server()
        except ConnetionClosedError:
            pass
        finally:
            await self.stop_routines()
    

   