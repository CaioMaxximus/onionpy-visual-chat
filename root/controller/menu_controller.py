import threading
import queue
from models.notification import Notification , NotificationType
class MenuController:

    def __init__(self, tor_manager,data_queue ,  notification_queue) -> None:
        self.function_queue = queue.Queue()
        self.tor_manager = tor_manager
        self.data_queue = data_queue
        self.notification_queue = notification_queue
        self.gui_loop = None
    
    def start_proxy(self, callback=None):
        self.function_queue.put(
            (lambda: self.tor_manager.start_tor_proxy(8), callback)
        )

    def get_my_servers(self, callback=None):
        self.function_queue.put(
            (lambda: self.tor_manager.check_server_conection(), callback)
        )

    def get_notification(self, callback=None):
        self.function_queue.put(
            (lambda: self._get_notification(), callback)
        )

    def create_new_onion_server(self, server_name, callback=None):
        self.function_queue.put(
            (lambda: self.tor_manager.create_new_onion_server(server_name), callback)
        )
    def run(self, gui_loop) -> None:
    
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target= self.check_function_queue, daemon=True)
            self.gui_loop = gui_loop
            self.thread.start()

    def _execute_callback(self,callback , *args):
        if callback is not None:
            self.gui_loop.call_soon_threadsafe(callback(*args))


    def _close(self) ->  None:
        if self.running:
            self.thread.join()

    def start_proxy(self,  callback=None):
        self.function_queue.put(
            lambda : self.tor_manager.start_tor_proxy(8)
            , callback)
    
    def get_my_servers(self ,  callback=None):
        self.function_queue.put(lambda : self.tor_manager.find_local_servers(),
                                callback)

    def get_notification(self, callback=None):
        self.function_queue.put(lambda : self._get_notification, callback)

    def _get_notification(self):
        res = None
        if len(self.notification_queue) > 0:
            return self.notification_queue.get()
        return res

    def create_new_onion_server(self,server_name, callback=None):
        self.function_queue.put(
            lambda : self.tor_manager.create_new_onion_server(server_name),
            callback)

    async def check_function_queue(self):
       while True:
            func, callback = await self.function_queue.get()
            try:
                res = func()
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

