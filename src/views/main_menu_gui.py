import customtkinter as ctk
from src.models.notification import  NotificationType
from popups import PopUpNotificationGUI  , PopUpEntryGui
from personalized_wigdets import ItemListView
from views.configuration_gui import ConfigurationGUI
from PIL import Image
from pathlib import Path

# HOST = '127.0.0.1'
# PORT = 8080

class MainMenuGUI:

    """
    Class representing the root view from the application.
    
    It allows to navigate to the server and clint view. Listing the alrady used 
    and availble  connecitons.

    Atributtes
    ----------
    root : ctk
        the root tkinter object for the all aplication
    controller : MenuController
        Worker that handles communication with the network layer and store the notifications
        to be collected by the -MainMenuGUI-
    client_gui_navigate : <function>
        A injected funciton from the ApplicationCoordinator to instanciate a new 
        ClientGUI class
    server_gui_navigate : <function>
        A injected funciton from the ApplicationCoordinator to instanciate a new 
        ServerGUI class
    
    Methods
    -------
    on_close()
        Gracefully shuts down the interface itself,the controller and the connection layer
    create_new_server
        Spawn a pop-up window to create a new server
    create_new_client
        Spawn a pop-up window to create a new client connection
    get_notification_routine
        Schedule a function to handle a notification after retrieved from the controller
    handle_notification
        Non blocking routine to colect stored notifcations for a proper exibition on the canvas
    create_new_server_window
        Calls the injected server_gui_navigate function to create a new server with the proper arguments
    create_new_client_window
        Calls the injected client_gui_navigate function with the proper arguments
    initiate_server_window
        Calls the injected server_gui_navigate function to iniate a new server with the proper arguments
    
    """

    def __init__(self,root , controller,
                 client_gui_navigate,server_gui_navigate):
        
        BASE_DIR = Path(__file__).resolve().parent     
        PROJECT_ROOT = BASE_DIR.parent     

        self.root = root
        self.root.geometry("630x630")
        self.root.title("ONION.PY VISUAL CHAT")
        self.controller = controller
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # self.start_screen()
        self.client_gui_navigate = client_gui_navigate
        self.server_gui_navigate = server_gui_navigate

        # set a purple background similar to the Tor symbol
        self.main_frame = ctk.CTkFrame(root)
        self.main_frame.pack(expand = True , fill="both")
        
        app_icon_img_path = PROJECT_ROOT / "assets" / "logo_onio_py.png"
        config_icon_img_path = PROJECT_ROOT / "assets" / "engrenagem.png"

        config_icon = ctk.CTkImage(light_image=(Image.open(config_icon_img_path)),
        size=(25, 25)
        )
        app_icon = ctk.CTkImage(light_image=(Image.open(app_icon_img_path)),
        size=(100, 100)
        )

        ## TOP FRAME
        self.top_frame = ctk.CTkFrame(self.main_frame)
        self.top_frame.pack(fill= "x")

        # self.label = ctk.CTkLabel(self.top_frame, text="WELCOME! What do you want to do now?")
        # self.label.pack(pady=30,side = "left")

        self.icon_app = ctk.CTkLabel(
        master=self.top_frame, 
        image=app_icon,  
        text="",height=50, width= 50
        )
        self.icon_app.pack(pady=20)
        
        self.config_btn = ctk.CTkButton(
            self.top_frame,
            text="",
            image=config_icon,
            width=30,
            height=30,
            fg_color="#6B2FB3",
            hover_color="#444",
            command=lambda:self.open_configarion()
        )
        self.config_btn.pack(pady = 30)


        # MIDLLE FRAME
        self.createServerBtn = ctk.CTkButton(self.main_frame, text = "Create a new server",
                                             command= self.create_new_server, fg_color="#6B2FB3")
        self.createServerBtn.pack(pady = 20)

        self.enterServerBtn = ctk.CTkButton(self.main_frame, text = "Enter in a new server",
                                            command= self.create_new_client, fg_color="#6B2FB3")
        self.enterServerBtn.pack(pady = 20)
        
        self.bottow_frame = ctk.CTkFrame(self.main_frame)
        self.bottow_frame.pack(fill="both")

        self.bottom_label = ctk.CTkLabel(self.bottow_frame,height=40,text="Start preloaded connections",fg_color="#6B2FB3")
        self.bottom_label.pack(fill = "x",pady = 20)

        # use the correctly spelled callback name
        self.my_servers_list = ItemListView(self.bottow_frame, "My servers", self.initiate_server_window, 
                                            lambda server : server.name)
        self.my_servers_list.pack(side = "left", fill = "y" , padx=10, pady=10)

        self.my_visited_servers_list = ItemListView(self.bottow_frame,"My discovered servers", self.initiate_client_window,
                                                    lambda server : (f"{server.name} + {server.hostname}"))
        self.my_visited_servers_list.pack(side = "right", fill = "y", padx=10, pady=10)
        self.controller.run(self.root,self.create_tables)

    def create_tables(self):
        def fecth_local_data(*args):
            self.controller.get_servers(lambda servers: self.my_servers_list.update_items(servers) )
            self.controller.get_discovered_servers(lambda servers_info: self.my_visited_servers_list.update_items(servers_info) )
            self.get_notification_routine()
            
        self.controller.start_tables(fecth_local_data)

        # self.open_configarion()

    def on_close(self):
            self.controller.end_tor(callback = lambda _ : self.root.destroy())
            

    def create_new_server(self):

        password_label_message = "Insert the password if the server has strict acess otherwise leave it blank.\n " \
        "Minimum of 8 characters," \
        " at least 1 uppercase letter, " \
        "1 lowercase letter, 1 number, and 1 special character; any blank space after or before will be removed!"

        pop_w = PopUpEntryGui(self.root,
                               ["Define a name for the new server",
                                 password_label_message]
                              , ["server_name", "password"])
        self.root.wait_window(pop_w)
        server_name = pop_w.registered_values["server_name"]
        password = pop_w.registered_values["password"]
        self.create_new_server_window(server_name , password)
    
    def create_new_client(self):
        pop_w = PopUpEntryGui(self.root,
                              ["Enter the Server Adress" ,"Enter the onion port", "Insert a password if the server has strict acess"],
                              ["onion_adress" ,"onion_port" , "password"])
        self.root.wait_window(pop_w)
        if pop_w.done:
            host = pop_w.registered_values["onion_adress"]
            port = pop_w.registered_values["onion_port"]
            port = port if port.strip(" ") != ""  else "-1"
            password = pop_w.registered_values["password"].strip(" ")


            self.create_new_client_window(host, port,password)


    def get_notification_routine(self):
        self.controller.get_notification(self.handle_notification)
    
    def handle_notification(self, notificaton):
        if notificaton is not None:
            n_type = notificaton.message_type
            msg = notificaton.content
            PopUpNotificationGUI(self.root, msg,n_type)
        self.root.after(10 , self.get_notification_routine)


    def create_new_server_window(self , server_name, password):
        self.server_gui_navigate(self.root , server_name ,mode = True,password = password)

    def create_new_client_window(self,host , port, password):
        self.client_gui_navigate(self.root , 0 , host ,port,password)

    def initiate_server_window(self, server):
        self.server_gui_navigate(self.root, server.name, mode=False,password = server.password)
    
    def initiate_client_window(self, server_info):
        
        pop_w = PopUpEntryGui(self.root,
                              ["Insert the password if the server has strict acess otherwise leave it blank"],
                              ["password"])
        self.root.wait_window(pop_w)
        self.client_gui_navigate(self.root,0 ,server_info.hostname, server_info.port, password = pop_w.registered_values["password"])


    # i will move this to application coordinato
    def open_configarion(self):
        self.config_view = ConfigurationGUI(self.root ,self.main_frame ,  self.controller)
        self.config_view.place(relx=0, rely=0, relwidth=1, relheight=1)
        # config_view.tkraise()


# ## REMOVED
# class ElementList(ctk.CTkScrollableFrame):

#     """
#     A class represeting a wigdet of a list of elements

#     It stores all the elements with a callback funtion associated for all of them. 
    
#     Attributes
#     ----------
#     master :  ctk
#         the root tkinter object for the all aplication
#     callback : <function>
#         Callback function that is called for one item of item once is clicked
#     items : list
#         Items used to polute the wigdet
#     buttons : {CTkButton}
#         Dictionary containing the buttons wigdets
    
#     Methods
#     ------
#     polute_frame
#         Instanciate the wigdets on the canvas
#     set_items
#         Allows lazy creation of the items on the list
#     """

#     def __init__(self, master, callback, items = []):
#         super().__init__(master)
#         self.master = master
#         self.callback = callback
#         self.items = items
#         self.buttons = {}
#         self.polute_frame()
    
#     def polute_frame(self):
#         for i, e in enumerate(self.items):
#             btn =  ctk.CTkButton(self,20,15,corner_radius= 8,
#                                              command= lambda e = e: self.callback(e),
#                                              text=e)
#             btn.pack(fill = "x")
#             self.buttons[i] = btn
    

#     def set_items(self,items):
#         self.items = items
#         self.polute_frame()


