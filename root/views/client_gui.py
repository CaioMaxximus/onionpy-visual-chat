import customtkinter as ctk
import  queue
import threading
import time
import random
from components.MessageFrame import  MessageFrame
from views.popup_entry_gui import PopUPEntryGui
from root.models.notification import NotificationType
# import socket
import asyncio
HOST = '127.0.0.1'
PORT = 8080

class ClientGUI(ctk.CTkToplevel):

    def __init__(self ,master, index , controler,data_queue , notification_queue):
        super().__init__(master)
        self.width = 400
        self.height = 400
        self.geometry(f"{self.height}x{self.width}")
        self.gui_queue =data_queue
        self.title("CLIENT SERVER")
        self._on_start()


        self.destroyed = False
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.notification_queue = notification_queue

        ## SERVER
        self.controler =  controler
        

        self.stop_thread_event = threading.Event()

        self.master.after(100 , self.check_queue_for_gui)
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


    def _on_close(self):
        # self.stop_thread_event.set()
        # self.web_thread.join()
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

    # def remove_guest(self,name):
    #     print("removing guest!")

    def scroll_to_bottom(self):
        self.scroll_frame._parent_canvas.yview_moveto(1.0)

    def check_queue_for_gui(self):
        try:
            # print("checkando a queue")
            while True:
                next_message = self.gui_queue.get(block=False)
                self.add_message_on_gui(**next_message)
        except queue.Empty:
            # print("sem melnsagens na fila")
            pass
        finally:
            if not self.destroyed : self.master.after(800 , self.check_queue_for_gui)

        
    def add_my_message(self):
        last_message = self.message_entry_bottom.get("1.0", "end-1c")
        self.message_entry_bottom.delete("1.0", "end") 
        
        self.controler.send_message_to_web(last_message)
        self.gui_queue.put({"entry" : last_message,
                             "author_name" : " " , "owner" :  True })
        
