import customtkinter as ctk
from models.notification import  NotificationType
from popups import PopUpNotificationGUI  , PopUpEntryGui
# HOST = '127.0.0.1'
# PORT = 8080

class MainMenuGUI:

    def __init__(self,root , controller,
                 client_gui_navigate,server_gui_navigate):
        
        self.root = root
        self.root.geometry("630x630")
        self.root.title("ONION.PY VISUAL CHAT")
        self.controller = controller
        self.controller.run(self.root)
        self.get_notification_routine()
        # self.start_screen()
        self.client_gui_navigate = client_gui_navigate
        self.server_gui_navigate = server_gui_navigate


        self.label = ctk.CTkLabel(root, text="WELCOLME! what do you wanna do now?")
        self.label.pack(pady = 30)

        self.createServerBtn = ctk.CTkButton(root, text = "Create a new server",
                                             command= self.create_new_server)
        self.createServerBtn.pack(pady = 20)

        self.enterServerBtn = ctk.CTkButton(root, text = "Enter in a new server",
                                            command= self.create_new_client_window)
        self.enterServerBtn.pack(pady = 20)
        
        self.bottow_frame = ctk.CTkFrame(self.root)
        self.bottow_frame.pack(fill="both")

        self.my_servers_list = ElementList(self.bottow_frame,self.iniatiate_server_window)
        self.my_servers_list.pack(side = "left", fill = "y" , padx=10, pady=10)

        self.my_visited_servers_list = ElementList(self.bottow_frame,print)
        self.my_visited_servers_list.pack(side = "right", fill = "y", padx=10, pady=10)

        self.controller.get_my_servers(lambda servers_names: self.my_servers_list.set_items(servers_names) )
        self.controller.get_my_servers(lambda servers_names: self.my_visited_servers_list.set_items(servers_names) )
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)



    def on_close(self):
            self.controller.end_tor(callback = lambda _ : self.root.destroy())
            

    def create_new_server(self):
        pop_w = PopUpEntryGui(self.root, ["Define a name for the new server"], ["server_name"])
        self.root.wait_window(pop_w)
        server_name = pop_w.registered_values["server_name"]
        self.create_new_server_window(server_name)

        # self.controller.create_new_onion_server(
        #     server_name , 
        #     lambda  : self.create_new_server_window(server_name))
    
    def create_a_new_client(self):
        # pop_w = PopUPEntryGui(self.root, ["HOST" , "PORT"], ["host" , "port"])
        # self.root.wait_window(pop_w)
        # host , port = pop_w.registered_values.values()
        self.create_new_client_window()

    # def start_onion_server(self, server_name):
    #     self.control.start_onion_server(server_name , lambda _ : self.create_new_server_window(server_name))
 
    def get_notification_routine(self):
        self.controller.get_notification(self.handle_notification)
    
    def handle_notification(self, notificaton):
        if notificaton is not None:
            n_type = notificaton.message_type
            msg = notificaton.content
            PopUpNotificationGUI(self.root, msg,n_type)
        self.root.after(10 , self.get_notification_routine)


    def create_new_server_window(self , server_name):
        self.server_gui_navigate(self.root , server_name ,mode = True)

    def create_new_client_window(self):
        self.client_gui_navigate(self.root , 0)

    def iniatiate_server_window(self, *args):
        self.server_gui_navigate(self.root , *args ,mode = False)

class ElementList(ctk.CTkScrollableFrame):

    def __init__(self, master, callback, items = []):
        super().__init__(master)
        self.master = master
        self.callback = callback
        self.items = items
        self.buttons = {}
        self.polute_frame()
    
    def polute_frame(self):
        for i, e in enumerate(self.items):
            btn =  ctk.CTkButton(self,20,15,corner_radius= 8,
                                             command= lambda e = e: self.callback(e),
                                             text=e)
            btn.pack(fill = "x")
            self.buttons[i] = btn
    

    def set_items(self,items):
        self.items = items
        self.polute_frame()


            