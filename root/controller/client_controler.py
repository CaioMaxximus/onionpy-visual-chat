import queue
import asyncio
from root.models.notification import Notification , NotificationType
import threading


class ClientController:

    def __init__(self,
                 connection, data_queue,
                 notification_queue,
                 ) -> None:

        self.client_connection = connection(
            self._insert_message_in_queue,
            self._insert_notification_in_queue)
        self.data_queue = data_queue
        self.notification_queue = notification_queue
        self.function_queue = queue.Queue()
        # self.thread = threading.Thread(target=self.run.s, daemon=True)
        self.HOST = None
        self.PORT = None
        self.running =  False

    def run(self, host: str, port: int) -> None:
        def start_event_loop():
            asyncio.run(self.root_process())
        
        if not self.running:
            self.HOST = host
            self.PORT = port
            self.running = True
            thread = threading.Thread(target=start_event_loop, daemon=True)
            thread.start()

    # async def root_process(self):
    #     await asyncio.gather(self.start_connection(), self.check_function_queue())

    async def check_function_queue(self):
        async def wrapped(func ,callback):
            try:
                res = await func()
            except (ConnectionError, TimeoutError):
                self.notification_queue.put(
                    Notification(NotificationType.WARNING, f"Fail executing {func.__name__}")
                )
            except Exception as e:
                self.notification_queue.put(
                    Notification(NotificationType.ERROR, f"Error executing {func.__name__}: {str(e)}")
                )
            else:
                self._execute_callback(callback , res)

        while True:
            func, callback = await self.function_queue.get()
            asyncio.create_task((wrapped(func , callback)))
            

    def _execute_callback(self,callback , *args):
        if callback is not None:
            self.gui_loop.call_soon_threadsafe(callback(*args))


    async def _start_connection(self) -> None:
        try:
            self.notification_queue.put(
                Notification(NotificationType.WARNING, "Connecting to server...")
            )
            await self.client_connection.async_server(self.HOST, self.PORT)
        except Exception as e:
            self.notification_queue.put(
                Notification(NotificationType.ERROR, str(e))
            )
            self.notification_queue.put(
                Notification(NotificationType.ERROR, "Connection failed! Aborting...")
            )
        self.notification_queue.put(
            Notification(NotificationType.WARNING, "Connection closed permanently.")
        )

    def send_message_to_web(self, message: str) -> None:
        self.function_queue.put(lambda : self.client_connection.add_message_to_send(message))

    def _insert_message_in_queue(self, message: str) -> None:
        self.data_queue.put(message)
        

    def _insert_notification_in_queue(self, notification: str) -> None:
        self.notification_queue.put( notification)

    def start_connection