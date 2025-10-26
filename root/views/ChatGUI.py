import customtkinter as ctk
import  queue
import threading
import time
import random
# import socket
import asyncio
from connection.ServerConnection import ServerConnection

class ServerGUI(ctk.CTkToplevel):

    def __init__(self ,master):

        ## SERVER
        self.top_info = ctk.CTkLabel(self,text= "Numero de usuarios ativos : 0")
        self.top_info.pack(pady = 3)

        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Lista de elementos")
        self.scroll_frame.pack(expand=True, fill="both", padx=10, pady=10)

        self.insert_message_btn = ctk.CTkButton(self, text = "enter", command= (self.add_my_message) 
                                                , width= min((self.width * 0.45),175 ))
        self.insert_message_btn.pack(side = "bottom" , pady = 5)

        self.message_entry_bottom =  ctk.CTkTextbox(self, font = ("Elvetica" ,12), 
                                                  width=  min((self.width * 0.75),200 ),
                                                  height= self.height * 0.15)
        self.message_entry_bottom.pack(side = "bottom" , pady = 5)

        self.stop_thread_event = threading.Event()

        self.master.after(100 , self.check_queue_for_gui)
        self.server_thread = threading.Thread(target = self.server.async_server, daemon= True)
        self.server_thread.start()


    def on_close(self):
        self.stop_thread_event.set()
        # self.web_thread.join()
        self.destroyed = True
        print("fechei a janela!")
        self.destroy()

    
    def add_message_on_gui(self , entry = "", author_name = " " , owner =  False ):
 
        author_name = "you" if owner else author_name
        side_gap = self.width * 0.1
        box = ctk.CTkFrame(self.scroll_frame, fg_color=("#2b2b2b" if not owner else "#006969"), corner_radius=10)
        box.pack(padx= ((side_gap,0) if not owner else (0,side_gap)), 
                 pady=10, fill = "x")

        # Primeiro label
        label1 = ctk.CTkLabel(box, text=f"UserName: {author_name}", font=("Arial", 8, "bold"))
        label1.pack(anchor="w", pady=(10, 0))

        # Segundo label
        label2 = ctk.CTkLabel(box, text=entry, font=("Arial", 12))
        label2.pack(anchor="w", pady=(0, 10))
        self.after(90 , self.scroll_to_bottom)

    def scroll_to_bottom(self):
        self.scroll_frame._parent_canvas.yview_moveto(1.0)

    def check_queue_for_gui(self):
        try:
            # print("checkando a queue")
            while True:
                next_message = self.gui_queue.get(block=False)
                self.add_message_on_gui(**next_message)
        except queue.Empty:
            print("sem melnsagens na fila")
        finally:
            if not self.destroyed : self.master.after(800 , self.check_queue_for_gui)

        

    def add_my_message(self):
        last_message = self.message_entry_bottom.get()
        self.message_entry_bottom.delete(0 ,len(last_message)) 
        
        self.server.add_message(last_message)
        self.gui_queue.put({"entry" : last_message,
                             "author_name" : " " , "owner" :  True })
        
