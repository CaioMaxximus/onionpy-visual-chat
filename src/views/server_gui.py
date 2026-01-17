import customtkinter as ctk
import  queue
import threading
from .basic_chat_view import BasicChatView


class ServerGUI(BasicChatView):

    def __init__(self ,master, name ,index,controller  ,creator_mode = False , ):
        super().__init__(master , controller)
        def step2(): ## Temporary here
            print("coloquei na pilha uma funcao")
            if creator_mode :
                self.controller.create_server(name , self._build_interface)
            else: 
                self.controller.start_server(name, self._build_interface)
            self.start_routines()

        self.HOST = None
        self.PORT = None
        self.name = name
        self.active_notification_gui = None


        self.controller.run(self.master , lambda : step2())
        self.destroyed = False
        



    def _build_interface(self, onion_connecion):
        super().build_interface()
        self.onion_connecion = onion_connecion
        # store server info and show a small top label
        host_info = f"{onion_connecion.hostname}:{onion_connecion.onion_port}"
        port_text = f"Serving on local port : {onion_connecion.local_port}"

        self.title(onion_connecion.server_name)
        self.top_info.configure(text=host_info)
        # try to update the scroll frame's label if it exists, otherwise keep a fallback attribute
        self.scroll_frame.configure(label_text=port_text)

        end_server_btn = ctk.CTkButton(self, width=20 , height=20,text = "TURN OFF SERVER",
                                       command= self.end_server)
        end_server_btn.pack(side ="top")

    def end_server(self):
        self.controller.close_server(lambda b: print("server closed!!"))