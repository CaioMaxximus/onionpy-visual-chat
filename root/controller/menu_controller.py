import threading
import queue
from models.notification import Notification , NotificationType
from connection.tor_service_manager2 import TorServiceManager
from data_base import db_service_manager as db
import asyncio


class MenuController:

    def __init__(self) -> None:
        self.function_queue = queue.Queue()
        self.data_queue = queue.Queue()
        self.notification_queue = queue.Queue()
        self.gui_loop = None
        self.running = False
      
    
    def _start_tor_service(self):
        TorServiceManager.start_tor(8)

    def get_my_servers(self, callback=None):
        self._enqueue(func=self._get_my_servers, callback= callback)

    def _get_my_servers(self):
        return TorServiceManager.find_local_servers()
    
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
            self.thread = threading.Thread(target= self.check_function_queue, daemon=True)
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

    # def create_new_onion_server(self,server_name, callback=None):
    #     self._enqueue(
    #          self._create_new_onion_server, 
    #         server_name,
    #         callback = callback)

    # def _create_new_onion_server(self, server_name):
    #     TorServiceManager.create_new_onion_server(server_name)
    #     port = asyncio.run(db.save_server(server_name))

    def _enqueue(self, func, *args, callback=None):
        try:
            self.function_queue.put_nowait((func, args, callback))
        except Exception:
            pass
        
    def check_function_queue(self):
        
       while True:
            func, args , callback = self.function_queue.get()
            try:
                res = func(*args)
            except (ConnectionError, TimeoutError) as e:
                self.notification_queue.put(
                    Notification(NotificationType.ERROR, str(e))
                )
            except FileNotFoundError as e:
                self.notification_queue.put(
                    Notification(NotificationType.ERROR, str(e))
                )
            else:
                self._execute_callback(callback , res)

