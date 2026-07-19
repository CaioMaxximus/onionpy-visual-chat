import asyncio
import re
## Temporary
class InvalidOnionHost(Exception): pass
class InvalidPort(Exception): pass

class ClientService():

    def __init__(self, connection, database_service, tor_service,notification_bus):
        self.connection = connection
        self.database_service = database_service
        self.tor_service = tor_service
        self.connected = False
        self.notification_bus = notification_bus


    async  def start(self, HOST ,  PORT):
        # self.message_queue = asyncio.Queue()
        # self.notification_queue = asyncio.Queue()
        self.HOST = HOST
        self.PORT = PORT
        self.connection.initialize()


    async def _close_connection(self) -> None:
        if self.connection._connected:
            await self.connection.close_connection()
        else:
            raise ConnectionError("The connection is already closed!")
        self.connected = False
        
    def validate_onion_and_port(self ,host: str, port: int):

        host = host.strip().lower()

        if not host.endswith(".onion"):
            raise InvalidOnionHost("Hostname must end with '.onion'.")

        name = host[:-6]  # remove ".onion"

        # v3: 56 chars base32 (a-z2-7)
        if len(name) != 56:
            raise InvalidOnionHost("Invalid Onion name, it must have 56 characters")

        if not re.fullmatch(r"[a-z2-7]+", name):
            raise InvalidOnionHost("Invalid Onion name: it must be base32 [a-z2-7].")

        try:
            port = int(port)
            
        except (TypeError, ValueError):
            raise InvalidPort("Port number must be an Integer")

        if not (1 <= port <= 65535):
            raise InvalidPort("Invalid interval number for the port (1–65535).")

   

    async def _start_client(self,name) -> None:
        
        self.validate_onion_and_port(self.HOST, self.PORT)
        server_handshake_data = await self.connection.run(name,self.HOST, self.PORT)
        # await self.start_routines()
        self.connected = True
        ## DEFINE A WAY TO NAME SERVER , FOR A WHILE, THE SAME NAME 
        await self.database_service.save_discovered_server(self.HOST, self.PORT,server_name = server_handshake_data["name"])
        return server_handshake_data
    async def get_message(self):
        return await self.connection.get_message_in_queue()
    
    async def send_message(self, message):
        await self.connection.send_message(message)