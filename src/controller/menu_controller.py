import threading
import queue
from models.notification import Notification , NotificationType
from src.connection.tor_service_manager import TorServiceManager
from data_base import repository
import asyncio


#  This controller will become asynchronus soon..
class MenuController:

    """
        Coordinates a background thread that dispatches tasks, enabling asynchronous
        communication between the UI and the network layer.

        Handles callbacks and notifications between both layers.

        Attributes
        ----------

        function_queue : Queue
            Stores the tasks asynchronous scheduled by the UI layer
        notification_queue : Queue
            Stores the notification to be collected by the UI layer
        gui_loop : ctk
            The root tkinter object for the all aplication, used to execute the callbacks 
            in the tkinter event loop
        runnig : Bool
            Represents the state of the controller

        Methods
        -------
        The methods that have a '_' underscore start version,are just the public version 
        of their counter part, using the queue to schedule theirs private selfs.
        
        _start_tor_service:
            Synchronusly start the tor service responsible for create all the application 
            connections
        _get_my_servers
    """

    def __init__(self) -> None:
        self.function_queue = queue.Queue()
        self.notification_queue = queue.Queue()
        self.gui_loop = None
        self.running = False
        self.tor_start_timeout = 15
      
    
    def _start_tor_service(self):
        TorServiceManager.start_tor(self.tor_start_timeout)

    def get_my_servers(self, callback=None):
        self._enqueue(func=self._get_my_servers, callback= callback)

    def remove_server(self,server_name , callback = None):
        self._enqueue(self._remove_server,server_name, callback = callback)

    def _get_my_servers(self):
        return asyncio.run(repository.get_all_servers())

    def _remove_server(self, server_name):
        asyncio.run(repository.remove_server(server_name))
    
    def get_discovered_servers(self ,callback):
        self._enqueue(func=self._get_discovered_servers,callback= callback)


    def get_notification(self, callback=None):
        self._enqueue(self._get_notification, callback = callback)
        
    def create_new_onion_server(self, server_name, callback=None):
        self._enqueue(
            (lambda: TorServiceManager.create_new_onion_server(server_name),
             (), callback)
        )
    def run(self, gui_loop) -> None:
    
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target= self.function_dispatcher, daemon=True)
            self.gui_loop = gui_loop
            self._enqueue(self._start_tor_service)
            self.thread.start()

    def _execute_callback(self,callback , res):
        if callback is not None:
            self.gui_loop.after(10,callback, res)


    def _close(self) ->  None:
        if self.running:
            self.thread.join()

    def start_proxy(self,  callback=None):
        self._enqueue(
             TorServiceManager.start_tor ,8)
        
    def end_tor(self, callback = None):
        self._enqueue(
             TorServiceManager.end_tor,callback = callback)

    def _get_notification(self):
        res = None
        if self.notification_queue.qsize() > 0:
            return self.notification_queue.get()
        return res

    def _enqueue(self, func, *args, callback=None):
        try:
            self.function_queue.put_nowait((func, args, callback))
        except Exception:
            pass

    ## This funciton will act this way, while the class have few async functions 
    ## an it was designed to be sync, prob will change in the future

    def _get_discovered_servers(self):
        return asyncio.run(repository.get_all_discovered_servers())

    
    def function_executer(self,func, args , callback ):
        try:
            res = func(*args)
        except (ConnectionError, TimeoutError ,FileNotFoundError , RuntimeError) as e:
            self.notification_queue.put(
                Notification(NotificationType.ERROR, str(e))
            )
        except Exception as e :
            error_message = "An unexpected error occurred, please reestart the application."
            self.notification_queue.put(
                Notification(NotificationType.ERROR ,str(e) + f"\n {error_message}" )
            )

        else:
            self._execute_callback(callback , res)
    
    def function_dispatcher(self):
        
       while self.running:
            func, args , callback = self.function_queue.get()
            self.function_executer(func, args , callback)
           

