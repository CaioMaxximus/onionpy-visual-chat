from .basic_chat_view import BasicChatView

class ClientGUI(BasicChatView):

    """
        The class represents the client side chat interface.

        It add to the base class behaviour by establishing his own
        schedule of actions to perform in the initialization process
        and some visual changes
    """

    def __init__(self ,master, name , controller, host , port):

        super().__init__(master , controller)
        self.host = host
        self.port = port
        self.controller =  controller
        self.master = master
        self.title("Client Onion conneciton")
        self.name = name

        
        def _on_start(self): 
            def started_callback():
                self.start_routines()
                self.running = True
                self.controller.start_client(name ,lambda server_data : self.build_interface(server_data))
            self.controller.run(self.host,self.port , self.master , started_callback)
        _on_start(self)
    


    def build_interface(self,server_data):
        super().build_interface()
        host_info = f"{server_data['name']} \n Connected to : \n {self.host}:{self.port}"
        self.title(f"Active chat : {self.host[0:10]}...")
        self.top_info.configure(text=host_info)
