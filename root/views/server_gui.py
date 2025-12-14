import customtkinter as ctk
import  queue
import threading
from components.message_frame import MessageFrame
from popups import PopUpNotificationGUI  , PopUpEntryGui


class ServerGUI(ctk.CTkToplevel):

    def __init__(self ,master, name ,index,controller  ,creator_mode = False , ):
        super().__init__(master)
        def step2():
            print("coloquei na pilha uma funcao")
            if creator_mode :
                self.controller.create_server(name , self.build_interface)
            else: 
                self.controller.start_server(name, self.build_interface)
            self.start_routines()

        self.HOST = None
        self.PORT = None
        self.name = name
        self.width = 400
        self.height = 400
        self.geometry(f"{self.height}x{self.width}")
        self.title("WEB SERVER")
        self.active_notification_gui = None

        self.message_queue = queue.Queue()
        self.notifications_queue = queue.Queue()
        self.controller = controller
        self.controller.run(self.master , lambda : step2())
        

    def start_routines(self):
        self.master.after(1000,self.get_message_routine)
        self.master.after(1000,self.get_notification_routine)
        self.master.after(1000,self.handle_notification)
        self.master.after(1000,self.handle_message)


    def build_interface(self, host = "lala" , port = "papa"):

        self.HOST = host
        self.PORT = port
        self.destroyed = False
        self.protocol("WM_DELETE_WINDOW", self.on_close)

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

        self.stop_thread_event = threading.Event()


    def on_close(self):
        self.stop_thread_event.set()
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

    def scroll_to_bottom(self):
        self.scroll_frame._parent_canvas.yview_moveto(1.0)

    def add_my_message(self):
        last_message = self.message_entry_bottom.get("1.0", "end-1c")
        self.message_entry_bottom.delete("1.0", "end") 
        
        self.controller.send_message_to_web(last_message)
        self.message_queue.put({"entry" : last_message,
                             "author_name" : " " , "owner" :  True })


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
        def change_state():
            self.active_notification_gui = None

        try:
            notificaton = self.notifications_queue.get(block=False)
            if notificaton is not None:
                
                n_type = notificaton.message_type
                msg = notificaton.content
                if self.active_notification_gui is not None:

                    self.master.after(2000, self.active_notification_gui.set_message, msg)
                else:
                    self.active_notification_gui = PopUpNotificationGUI(
                        self, msg,
                        callback = lambda :  change_state)
                    # self.wait_window(self.active_notification_gui)
                    # self.active_notification_gui = None
        except queue.Empty:
            pass
        finally:   # print("vazia")
            if not self.destroyed : self.master.after(10 , self.handle_notification)

    def handle_message(self):
        try:
            next_message = self.message_queue.get(block=False)
            self.add_message_on_gui(**next_message)
        except queue.Empty:
            # print("sem melnsagens na fila")
            pass
        finally:
            if not self.destroyed : self.master.after(10 , self.handle_message)

        