import asyncio

class ClientConnection():
    def __init__(self, messages_queue, HOST , PORT , pin = None):
        self.users = []
        self.pin = pin
        self.messages_queue = messages_queue
        self.HOST = HOST
        self.PORT = PORT
        print(HOST , PORT)
        print("parametros")


    def delete_user(self, user_id):
        self.users.remove(user_id)
        self.local_black_list.append()
    
    def async_server(self):
        async def events():
            self.web_loop = asyncio.get_event_loop()
            await asyncio.gather(self.server_connection() ,self.check_messages_for_web())
        
        asyncio.run(events())
    
    async def check_messages_for_web(self):
        while True:
            last_message = await self.web_queue.get()
            await self.send_message(last_message)

    async def server_connection(self):

        async def connection_handler(reader, writer):
            async def local_listerner(reader, writer):
                self.writer = writer
                while True:
                    data = await reader.read(1024)
                    if not data:
                        print("Servidor desconectado.")
                        break
                    message = data.decode().strip()
                    # print(f"==== chegou mensagem: {message}")
                    msg_info = {
                        "entry": message,
                        "author_name": str(writer.get_extra_info('peername')), 
                        "owner": False
                    }
                    # await self.web_queue.put(msg_info)
                    self.messages_queue.put(msg_info)
                    # self.add_message_on_gui(entry = message, author_name = " " , owner =  False)

            await local_listerner(reader , writer)
        
        self.web_queue = asyncio.Queue()
        # print("==========")
        # print(self.HOST)
        # print(self.PORT)
        try:
            reader,writer = await asyncio.open_connection( self.HOST , self.PORT)
        except :
            print("conexao falhou!")

        await connection_handler(reader,writer)


    
    async def send_message(self, message):
        data = message["entry"]
        data_encoded = (data + "\n").encode()
        w = self.writer

        try:
            w.write(data_encoded)
            await w.drain()
            print("a mensagem foi envida do cliente com sucesso!!")
        except (ConnectionResetError , ConnectionRefusedError): 
            print("erro de conexao")
        
    def add_message(self,message):
        self.web_loop.call_soon_threadsafe(self.web_queue.put_nowait , {"entry" : message,
                             "author_name" : " " , "owner" :  True })