from abc import ABC , abstractmethod
import asyncio
from src.models import Notification, NotificationType
from typing import Optional

class BaseConnection(ABC):

    def __init__(self, notification_bus):
            
            self.notification_bus = notification_bus
            self.messages_queue: Optional[asyncio.Queue] = None
            self._connected: bool = False
            self.server_task: Optional[asyncio.Task] = None
            self.writer = None
            

    def initialize(self) :

        self.messages_queue = asyncio.Queue()

    async def notify(self, level: NotificationType, message: str) -> None:
        await self.notification_bus.send(Notification(level, message))

    @abstractmethod
    async def run(self,*args, **kwargs) -> None:
         
        await self.startup()

    @abstractmethod
    async def send_message(self) -> None:
         raise NotImplementedError()
    

    async def get_message_in_queue(self):
        msg = await self.messages_queue.get()
        return msg
    

    @abstractmethod
    async def _handshake(self,reader,writer):
         raise NotImplementedError()

    def handle_tasks_errors(self, task):
         
        try:
        
            task.result()
        except asyncio.CancelledError:
            pass

        except Exception as e:
             
            ## Logg here
            print(e)
            pass
