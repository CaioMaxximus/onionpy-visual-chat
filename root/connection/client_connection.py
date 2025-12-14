import asyncio
from python_socks.async_.asyncio import Proxy
from python_socks import ProxyType
from models.notification import Notification , NotificationType


class ClientConnection():
    def __init__(self, pin = None):
        self.users = []
        self.pin = pin
        self.messages_queue = asyncio.Queue()
        self.notification_queue= asyncio.Queue()
        self.HOST  = None 
        self.PORT = None
        self.proxy_port = None
        self.sock = None
        self.writer = None  
        self.messages_to_send_queue = asyncio.Queue()
        self._connected = False

    def validate_connection_state(func):
        async def inner_wrapper(self ,*args, **kwargs):
            if self._connected:
                return await func(self,*args, **kwargs)
            else:
                raise ValueError("The connection didnt start yet!")
        return inner_wrapper
    

    async def run(self, host: str, port: int ,proxy_port) -> None:
        self.HOST = host
        self.PORT = port
        self.proxy_port = proxy_port
        await self.start_server_connection()

    @validate_connection_state
    async def end_connection(self):
        self._connected = False
        self.messages_checker_task.cancel()
        try:
            await self.messages_checker_task
        except :
            pass
        await self.notification_queue.put(Notification(NotificationType.WARNING,
                                          "Connection finished with the server."))
        

        
    @validate_connection_state    
    async def check_messages_for_web(self):
        while  True:
            try :
                last_message = await self.messages_to_send_queue.get()
                await self.send_message(last_message)
            except asyncio.CancelledError():
                pass

    @validate_connection_state
    async def connection_handler(self,reader, writer):
        self.writer = writer
        while True:
            data = await reader.read(4096)
            if not data:
                await self.notification_queue.put(
                    Notification(NotificationType.WARNING,"Connection closed by the server."))
                break
            message = data.decode().strip()
            msg_info = {
                "entry": message,
                "author_name": str(writer.get_extra_info('peername')), 
                "owner": False
            }
            await self.messages_queue.put(msg_info)

    async def start_server_connection(self):

        try:
            self.proxy = Proxy(proxy_type= ProxyType.SOCKS5,
                            host= "127.0.0.1" , port = self.proxy_port, rdns=True)
            self.sock  = await self.proxy.connect(dest_host = self.HOST,dest_port= self.PORT,
            )   
        except TimeoutError as e:
            raise RuntimeError(f"Connection timeout in proxy connection {self.HOST}:{self.PORT}") from e
        except ConnectionError as e:
            raise ConnectionError(f"Error! Unable to connect to proxy {self.HOST}:{self.PORT}") from e
        
        try :
            reader,writer = await asyncio.open_connection( 
                sock = self.sock)
            self._connected = True
        except TimeoutError:
            raise RuntimeError(f"Connection timeout trying to connect to server {self.HOST}:{self.PORT}")
        except ConnectionError as e:
            raise ConnectionError(f"Error! Unable to connect to server {self.HOST}:{self.PORT}") from e
        else:
            self.messages_checker_task = asyncio.create_task(self.check_messages_for_web())
            await self.connection_handler(reader,writer)
        await self.end_connection()
        
    @validate_connection_state
    async def send_message(self, message):
        data = message
        data_encoded = (data + "\n").encode()
        w = self.writer

        try:
            w.write(data_encoded)
            await w.drain()
            print("a mensagem foi envida do cliente com sucesso!!")
        except (ConnectionResetError , ConnectionRefusedError): 
            await self.notification_queue.put(
                Notification(NotificationType.WARNING , 
                "Unable to send the message , try again"))
        
    @validate_connection_state
    async def add_message_to_send(self,message):
        await self.messages_to_send_queue.put(message)
    
    @validate_connection_state
    async def get_message_in_queue(self):
        return await self.messages_queue.get()
    
    async def get_notification_in_queue(self):
        return await self.notification_queue.get()
    
    