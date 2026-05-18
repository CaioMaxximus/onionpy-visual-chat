import asyncio

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
        if self.connected:
            await self.connection.close_connection()
            self.connected = False
        else:
            raise ConnectionError("The connection is already closed!")
   

    async def _start_client(self) -> None:

        await self.connection.run(self.HOST, self.PORT)
        await self.start_routines()
        self.connected = True
        ## DEFINE A WAY TO NAME SERVER , FOR A WHILE, THE SAME NAME 
        await self.database_service.save_discovered_server_securely("NEW_CONNECTION",self.HOST ,self.PORT)

    async def get_message(self):
        return await self.connection.get_message_in_queue()
    
    async def send_message(self, message):
        await self.connection.send_message(message)