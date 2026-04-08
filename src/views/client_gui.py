import customtkinter as ctk
# import  queue
# import threading
# import time
# import random
# from components.message_frame import  MessageFrame
from popups import PopUpEntryGui
# from models.notification import NotificationType
from .basic_chat_view import BasicChatView

# HOST = '127.0.0.1'
# PORT = 8080

class ClientGUI(BasicChatView):

    """
        The class represents the client side chat interface.

        It add to the base class behaviour by establishing his own
        schedule of actions to perform in the initialization process
        and some visual changes
    """

    def __init__(self ,master, index , controller, host , port):

        super().__init__(master , controller)
        self.host = host
        self.port = port
        self.controller =  controller
        self.master = master
        self.title("Client Onion conneciton")

        
        def _on_start(self): 
            def started_callback():
                self.start_routines()
                self.running = True
                self.controller.start_client(lambda _ : self.build_interface())
            self.controller.run(self.host,self.port , self.master , started_callback)
        _on_start(self)
    


    def build_interface(self):
        super().build_interface()
        host_info = f"Connected to : \n {self.host}:{self.port}"
        self.title(f"Active chat : {self.host[0:10]}...")
        self.top_info.configure(text=host_info)
