import customtkinter as ctk
import  queue
import threading
import time
import random
from components.message_frame import  MessageFrame
from popups import PopUpEntryGui
from models.notification import NotificationType
# import socket
import asyncio
HOST = '127.0.0.1'
PORT = 8080

class ClientGUI(ctk.CTkToplevel):

    def __init__(self ,master, index , controler):
        super().__init__(master)
        self.width = 400
        self.height = 400
        self.geometry(f"{self.height}x{self.width}")
        self.title("CLIENT SERVER")
        self.notification_queue = queue.Queue()
        self.messages_queue = queue.Queue()
        self._on_start()
        # self.master.after(100 , self.check_queue_for_gui)


        self.destroyed = False
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        ## SERVER
        self.controler =  controler
        # self.stop_thread_event = threading.Event()

        # self.server_thread = threading.Thread(target = self.controler.async_server, daemon= True)
        # self.server_thread.start()

    def _on_start(self): 
        pop_w = PopUPEntryGui(self.master,["Enter the Server Adress"],["onion_adress"])
        self.wait_window(pop_w)
        host_port = pop_w.registered_values["onion_adress"].split(":")
        host = host_port[0]
        port = int(host_port[1]) if len(host_port) > 1  else 80
        self.message_loading_element = ctk.CTkTextbox(self, font = ("Elvetica" ,12),
                                                  width=  min(int(self.width * 0.75),200 ),
                                                  height= int(self.height * 0.15))
        self.message_loading_element.pack(side="top", pady=5, anchor="center")
        self.controler.run(host,port)
        self._wait_succed_connection()

    
    def collect_notification(self):
        def store_notification(notification):
            self.notification_queue.put(notification)
            self.after(100 , self.collect_notification)

        self.controler.get_notification(lambda res : store_notification(res))

    def collect_message(self):
        def store_message(msg):
            self.message_queue.put(msg)
            self.after(100 , self.collect_message)

        self.controler.get_web_message(lambda res : store_message(res))
    


    def _wait_succed_connection(self):
        if not self.notification_queue.empty():
            notification = self.notification_queue.get()
            self.message_loading_element.delete("1.0", "end")
            if notification.message_type == NotificationType.WARNING:
                self.message_loading_element.insert("end", f"{notification.content}\n")
                self.message_loading_element.see("end")
                self.after(100, self._wait_succed_connection)

            elif notification.message_type == NotificationType.ERROR:
                self.message_loading_element.insert("end", f"{notification.content}\n")
                self.message_loading_element.see("end")
                self.after(2000, self._on_close)

            elif notification.message_type == NotificationType.SUCCESS:
                self.message_loading_element.insert("end", f"{notification.content}\n")
                self.message_loading_element.see("end")
                self.after(1500, self.build_gui)
        else :
            self.after(2000, self.build_gui)


    def build_gui(self):
        self.top_info = ctk.CTkLabel(self,text= "Numero de usuarios ativos : 0")
        self.top_info.pack(pady = 3)

        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Lista de elementos")
        self.scroll_frame.pack(expand=True, fill="both", padx=10, pady=10)

        self.insert_message_btn = ctk.CTkButton(self, text = "enter", command= (self.add_my_message) 
                                                , width= min(int(self.width * 0.45),175 ))
        self.insert_message_btn.pack(side = "bottom" , pady = 5)

        self.message_entry_bottom =  ctk.CTkTextbox(self, font = ("Elvetica" ,12), 
                                                  width=  min(int(self.width * 0.75),200 ),
                                                  height= int(self.height * 0.15))
        self.message_entry_bottom.pack(side = "bottom" , pady = 5)
        self.collect_notification()
        self.collect_message()


    def _on_close(self):

        self.destroyed = True
        print("fechei a janela!")
        self.destroy()

    
    def add_message_on_gui(self , entry = "", author_name = " " , owner =  False ):
 
        author_name = "you" if owner else author_name
        side_gap = self.width * 0.1

        message_frame = MessageFrame(
            self.scroll_frame,
            author_name,
            content=entry,
            callback= print,
            fg_color=("#2b2b2b" if not owner else "#006969"),
            corner_radius=10
        )
        message_frame.pack(
            padx=((side_gap, 0) if not owner else (0, side_gap)),
            pady=10,
            fill="x",
            anchor="w"
        )

        self.after(90 , self.scroll_to_bottom)

    def scroll_to_bottom(self):
        self.scroll_frame._parent_canvas.yview_moveto(1.0)

    def check_messages_queue_for_gui(self):
        try:
            # print("checkando a queue")
            while True:
                next_message = self.messages_queue.get(block=False)
                self.add_message_on_gui(**next_message)
        except queue.Empty:
            # print("sem melnsagens na fila")
            pass
        finally:
            if not self.destroyed : self.master.after(800 , self.check_queue_for_gui)

        
    def add_my_message(self):

        def put_my_message_on_gui():
            self.messages_queue.put({"entry" : last_message,
                                "author_name" : " " , "owner" :  True })
        last_message = self.message_entry_bottom.get("1.0", "end-1c")
        self.message_entry_bottom.delete("1.0", "end")
        self.controler.send_message_to_web(last_message, lambda _ : put_my_message_on_gui())

        
