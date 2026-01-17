import customtkinter as  ctk
import queue
from popups import PopUpNotificationGUI  , PopUpEntryGui
from components.message_frame import MessageFrame
from models import NotificationType




class BasicChatView(ctk.CTkToplevel):
    
    def __init__(self , master,controller):
        super().__init__(master)
        self.master = master
        self.controller = controller
        self.message_queue = queue.Queue()
        self.notifications_queue = queue.Queue()
        self.protocol("WM_DELETE_WINDOW", self.on_close)


        self.width = 750
        self.height = 750
        self.geometry(f"{self.height}x{self.width}")


        
    def on_close(self):
        self.destroyed = True
        self.controller.close_controller()
        try:
            self.withdraw()  
        except Exception:
            pass
        # self.destroy()
        self.winfo_toplevel().destroy()

    def  build_interface(self):


        self.top_info = ctk.CTkLabel(self,text= "Numero de usuarios ativos : 0")
        self.top_info.pack(pady = 3)

        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Lista de elementos")
        self.scroll_frame.pack(expand=True, fill="both", padx=10, pady=10)

        self.insert_message_btn = ctk.CTkButton(self, text = "enter", command= self.add_my_message
                                                , width= min(int(self.width * 0.45),175 ))
        self.insert_message_btn.pack(side = "bottom" , pady = 5)

        self.message_entry_bottom =  ctk.CTkTextbox(self, font = ("Elvetica" ,12), 
                                                  width=  max(int(self.width * 0.65),200 ),
                                                  height= int(self.height * 0.15))
        self.message_entry_bottom.pack(side = "bottom" , pady = 5)


    def start_routines(self):
        self.master.after(1000,self.get_message_routine)
        self.master.after(1000,self.get_notification_routine)
        self.master.after(1000,self.handle_notification)
        self.master.after(1000,self.handle_message)

        # self.stop_thread_event = threading.Event()

    ## ROUTINES AREA
    
    ## a funcao so e chamda quando um item foi retornado do controller
    ## o controlle ropera em asyncio ent pode esperar pela fila 
    def get_notification_routine(self):
        
        def put_in_queue(notification):
            self.notifications_queue.put(notification)
            self.after(10 ,self.get_notification_routine)
        self.controller.get_notification(put_in_queue) 

    ## a funcao so e chamda quando um item foi retornado do controller
    ## o controlle ropera em asyncio ent pode esperar pela fila
    def get_message_routine(self):
        def put_in_queue(message):
            self.message_queue.put(message)
            self.after(10 ,self.get_message_routine)
        self.controller.get_web_message(put_in_queue)
    


    def handle_notification(self):
        def change_state(n_type):
            self.active_notification_gui = None
            if n_type == NotificationType.ERROR:
                self.on_close()

        try:
            notificaton = self.notifications_queue.get(block=False)                
            n_type = notificaton.message_type
            msg = notificaton.content

            if notificaton is not None and n_type != NotificationType.INFO:

                if self.active_notification_gui is not None:
                    self.active_notification_gui.callback  = lambda :  change_state(n_type)
                    self.master.after(2000, self.active_notification_gui.set_message, msg , n_type)
                   
                else:
                    self.active_notification_gui = PopUpNotificationGUI(
                        self, msg, n_type,
                        callback = lambda :  change_state(n_type))
                    # self.wait_window(self.active_notification_gui)
                    # self.active_notification_gui = None
                # self.wait_window(self.active_notification_gui)
        except queue.Empty:
            pass
        finally:  
            if not self.destroyed : self.master.after(10 , self.handle_notification)

    def handle_message(self):
        try:
            next_message = self.message_queue.get(block=False)
            self.add_message_on_gui(**next_message)
        except queue.Empty:
            # print("sem melnsagens na fila")
            pass
        finally:
            if not self.destroyed : self.master.after(50 , self.handle_message)


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


    def add_my_message(self):
        last_message = self.message_entry_bottom.get("1.0", "end-1c") + '\0'
        self.message_entry_bottom.delete("1.0", "end") 
        
        msg= {"entry" : last_message,
                             "author_name" : " " , "owner" :  True }

        self.controller.send_message_to_web(msg , None)
        self.message_queue.put(msg)

    def scroll_to_bottom(self):
        self.scroll_frame._parent_canvas.yview_moveto(1.0)