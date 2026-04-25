import customtkinter as ctk
import  queue
import threading
from .basic_chat_view import BasicChatView


class ServerGUI(BasicChatView):

    """
    Represents the server-side chat interface.

    Extends the base controller by defining its own initialization workflow
    and applying UI-specific customizations.

    Attributes
    ---------

    HOST : str
        The onion server hostname
    PORT : int
        The onion port
    name : str
        The server name, stored in the database
    

    """

    def __init__(self ,master, name ,index,controller  ,creator_mode = False ):
        super().__init__(master , controller)


        self.HOST = None
        self.PORT = None
        self.name = name
        self.creator_mode = creator_mode
        self.title("Server Onion conneciton")


        self.controller.run(self.master , lambda : self._start_server())
    
    def _start_server(self): ## Temporary here
        print("coloquei na pilha uma funcao")
        self.running = True
        print("server name no server guiu")
        print(self.name)
        if self.creator_mode :
            self.controller.create_server(self.name , self._build_interface)
        else: 
            self.controller.start_server(self.name, self._build_interface)
        # to notifications schedule must be already active to the server initialization
        self.start_routines() 


    def _build_interface(self, onion_connecion):
        super().build_interface()
        self.onion_connecion = onion_connecion
        host_info = f"{onion_connecion.hostname}:{onion_connecion.onion_port}"
        port_text = f"Serving on local port : {onion_connecion.local_server_port}"

        self.title(onion_connecion.name)
        self.top_info.configure(text=host_info)
        self.scroll_frame.configure(label_text=port_text)

        end_server_btn = ctk.CTkButton(self, width=20 , height=20,text = "TURN OFF SERVER",
                                       command= self.end_server)
        end_server_btn.pack(side ="top")

    def end_server(self):
        self.controller.close_server(lambda b: print("server closed!!")) ## add pop up