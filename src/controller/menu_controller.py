import threading
import queue
from models.notification import Notification , NotificationType
from src.connection.tor_service_manager import TorServiceManager
from data_base import repository
import asyncio
import inspect

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
        _get_servers
    """

    def __init__(self) -> None:
        self.gui_loop = None
        self.running = False
        self.tor_start_timeout = 15
        self.my_loop = None

    def run(self, gui_loop ,callback) -> None:
    
        if not self.running:
            self.thread = threading.Thread(target= self.start_event_loop,args=(callback , ) , daemon=True)
            self.gui_loop = gui_loop
            self.thread.start()

    def start_event_loop(self,callback): 

        async def start():
            self.function_queue = asyncio.Queue()
            self.notification_queue = asyncio.Queue()
            self.running = True
            self.my_loop = asyncio.get_running_loop()
            self._enqueue(self._start_tor_service)

            self.main_routine = asyncio.create_task(self.function_dispatcher())
            self.gui_loop.after(100,callback)
            await self.main_routine
    
        try:
            asyncio.run(start())
        except asyncio.CancelledError:
            pass
    
    def _start_tor_service(self):
        TorServiceManager.start_tor(self.tor_start_timeout)
    
    def start_tables(self, callback):
        self._enqueue(func = self._start_tables,callback=callback)
    
    async def _start_tables(self):
        await repository.create_tables()

    def get_servers(self, callback=None):
        self._enqueue(func=self._get_servers, callback= callback)

    def remove_server(self,server_name , callback = None):
        self._enqueue(self._remove_server,server_name, callback = callback)

    async def _get_servers(self):
        return await repository.get_all_servers()

    async def _remove_server(self, server_name):
       await repository.remove_server(server_name)
    
    def get_discovered_servers(self ,callback):
        self._enqueue(func=self._get_discovered_servers,callback= callback)

    def remove_discovered_server(self, hostname,callback):
        self._enqueue(self._remove_discovered_server,hostname,callback=callback)
    
    async def _get_discovered_servers(self):
        return await repository.get_all_discovered_servers()

    async def _remove_discovered_server(self,hostname):
        await repository.remove_discovered_server(hostname)
        print("")
        
    def get_notification(self, callback=None):
        self._enqueue(self._get_notification, callback = callback)
        
    def create_new_onion_server(self, server_name, callback=None):
        self._enqueue(
            (lambda: TorServiceManager.create_new_onion_server(server_name),
             (), callback)
        )

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

    async def _get_notification(self):
        
        return await self.notification_queue.get()

    def _enqueue(self, func, *args, callback=None):
        try:
            self.my_loop.call_soon_threadsafe(self.function_queue.put_nowait, (func, args, callback))
        except Exception as e:
            raise e

    ## This funciton will act this way, while the class have few async functions 
    ## an it was designed to be sync, prob will change in the future

    async def function_executer(self,func, args , callback):
        try:
            print(func.__name__)
            if inspect.iscoroutinefunction(func):
                print("é assinc")
                res = await func(*args)
            else:
                print("n é assinc")
                res = await asyncio.to_thread(func,*args) 

        except (ConnectionError, TimeoutError ,FileNotFoundError , RuntimeError) as e:
            await self.notification_queue.put(
                Notification(NotificationType.ERROR, str(e))
            )
        except Exception as e :
            error_message = "An unexpected error occurred, please reestart the application."
            await self.notification_queue.put(
                Notification(NotificationType.ERROR ,str(e) + f"\n {error_message}" )
            )
        else:
            print(res)
            print("vou chamar o callback")
            self._execute_callback(callback , res)
    
    async def function_dispatcher(self):
    
        print("o dispatcher foi iniciado!!")
        while self.running:
            func, args , callback = await self.function_queue.get()
            new_task = asyncio.create_task(self.function_executer(func, args , callback))
           

