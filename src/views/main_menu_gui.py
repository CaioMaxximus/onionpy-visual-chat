import customtkinter as ctk
from models.notification import  NotificationType
from popups import PopUpNotificationGUI  , PopUpEntryGui
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
        
        self.root = root
        self.root.geometry("630x630")
        self.root.title("ONION.PY VISUAL CHAT")
        self.controller = controller
        self.controller.run(self.root)
        self.get_notification_routine()
        # self.start_screen()
        self.client_gui_navigate = client_gui_navigate
        self.server_gui_navigate = server_gui_navigate


        # fixed text
        self.label = ctk.CTkLabel(root, text="WELCOME! What do you want to do now?")
        self.label.pack(pady=30)

        self.createServerBtn = ctk.CTkButton(root, text = "Create a new server",
                                             command= self.create_new_server)
        self.createServerBtn.pack(pady = 20)

        self.enterServerBtn = ctk.CTkButton(root, text = "Enter in a new server",
                                            command= self.create_new_client)
        self.enterServerBtn.pack(pady = 20)
        
        self.bottow_frame = ctk.CTkFrame(self.root)
        self.bottow_frame.pack(fill="both")

        # use the correctly spelled callback name
        self.my_servers_list = ElementList(self.bottow_frame, self.initiate_server_window)
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
    
    def create_new_client(self):
        pop_w = PopUpEntryGui(self.root,
                              ["Enter the Server Adress" ,"Enter the onion port"],
                              ["onion_adress" ,"onion_port"])
        self.root.wait_window(pop_w)
        if pop_w.done:
            host = pop_w.registered_values["onion_adress"]
            port = pop_w.registered_values["onion_port"]
            port = port if port.strip(" ") != ""  else "-1"

            self.create_new_client_window(host, port)

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

    def create_new_client_window(self,host , port):
        self.client_gui_navigate(self.root , 0 , host ,port)

    def initiate_server_window(self, *args):
        self.server_gui_navigate(self.root, *args, mode=False)

class ElementList(ctk.CTkScrollableFrame):

    """
    A class represeting a wigdet of a list of elements

    It stores all the elements with a callback funtion associated for all of them. 
    
    Attributes
    ----------
    master :  ctk
        the root tkinter object for the all aplication
    callback : <function>
        Callback function that is called for one item of item once is clicked
    items : list
        Items used to polute the wigdet
    buttons : {CTkButton}
        Dictionary containing the buttons wigdets
    
    Methods
    ------
    polute_frame
        Instanciate the wigdets on the canvas
    set_items
        Allows lazy creation of the items on the list
    """

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


