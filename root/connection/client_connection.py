import asyncio
from python_socks.async_.asyncio import Proxy
import ssl
from python_socks._types import ProxyType


class ClientConnection():
    def __init__(self,pin = None):
        self.users = []
        self.pin = pin
        self.on_messages_callback = None
        self.on_notification_callback = None
        self.HOST  = None 
        self.PORT = None
        self.sock = None
        self.web_loop = None
        self.writer = None
        self.web_queue = asyncio.Queue()


    def set_callbacks(self , on_messages_callback ,on_notification_callback):
        self.on_messages_callback = on_messages_callback
        self.on_notification_callback = on_notification_callback

    async def async_server(self, host: str, port: int) -> None:
        self.HOST = host
        self.PORT = port
        await asyncio.gather(self.server_connection() ,self.check_messages_for_web())
            
    async def check_messages_for_web(self):
        while True:
            last_message = await self.web_queue.get()
            await self.send_message(last_message)

    async def connection_handler(self,reader, writer):
        self.writer = writer
        while True:
            data = await reader.read()
            if not data:
                self.on_notification_callback("Connection closed by the server.")
                break
            message = data.decode().strip()
            msg_info = {
                "entry": message,
                "author_name": str(writer.get_extra_info('peername')), 
                "owner": False
            }
            self.on_messages_callback(msg_info)

    async def server_connection(self):


        try:
            self.proxy = Proxy(proxy_type= ProxyType.SOCKS5,
                            host= "127.0.0.1" , port = 9050, rdns=True)
            self.sock  = await self.proxy.connect(dest_host = self.HOST,dest_port= self.PORT,
            )
        except TimeoutError as e:
            raise RuntimeError(f"Connection timeout in proxy connection {self.HOST}:{self.PORT}") from e
        except ConnectionError as e:
            raise ConnectionError(f"Error! Unable to connect to proxy {self.HOST}:{self.PORT}") from e
        
        try :
            reader,writer = await asyncio.open_connection( 
                sock = self.sock)
        except TimeoutError:
            raise RuntimeError(f"Connection timeout trying to connect to server {self.HOST}:{self.PORT}")
        except ConnectionError as e:
            raise ConnectionError(f"Error! Unable to connect to server {self.HOST}:{self.PORT}") from e

        await self.connection_handler(reader,writer)
        

    async def send_message(self, message):
        data = message
        data_encoded = (data + "\n").encode()
        w = self.writer

        try:
            w.write(data_encoded)
            await w.drain()
            print("a mensagem foi envida do cliente com sucesso!!")
        except (ConnectionResetError , ConnectionRefusedError): 
            print("erro de conexao")
        
    async def add_message_to_send(self,message):
        await self.web_queue.put(message)
