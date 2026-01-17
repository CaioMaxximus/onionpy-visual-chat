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

    def __init__(self ,master, index , controller):
        super().__init__(master , controller)

        self.destroyed = False
        self.active_notification_gui = None

        # self.protocol("WM_DELETE_WINDOW", self._on_close)
        ## SERVER
        self.controller =  controller
        
        self.after(200,self._on_start)

    def _on_start(self): 
        def started_callback():
            self.start_routines()
            # self.collect_notification()
            # self.collect_message()
            self.controller.start_client(lambda _ : self.build_interface())
        
        pop_w = PopUpEntryGui(self.master,["Enter the Server Adress"],["onion_adress"])
        self.wait_window(pop_w)
        host_port = pop_w.registered_values["onion_adress"].split(":")
        self.host = host_port[0]
        self.port = int(host_port[1]) if len(host_port) > 1  else 80
        # self.message_loading_element = ctk.CTkTextbox(self, font = ("Elvetica" ,12),
        #                                           width=  min(int(self.width * 0.75),200 ),
        #                                           height= int(self.height * 0.15))
        # self.message_loading_element.pack(side="top", pady=5, anchor="center")
        self.controller.run(self.host,self.port , self.master , started_callback)
        # self.check_messages_queue_for_gui()
        # self._wait_succed_connection()


    def build_interface(self):
        super().build_interface()
        host_info = f"Connected to : \n {self.host}:{self.port}"
        self.title(f"Active chat : {self.host[0:10]}...")
        self.top_info.configure(text=host_info)
