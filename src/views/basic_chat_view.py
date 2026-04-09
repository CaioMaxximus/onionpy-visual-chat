import customtkinter as  ctk
import queue
from popups import PopUpNotificationGUI  , PopUpEntryGui
from components.message_frame import MessageFrame
from models import NotificationType




class BasicChatView(ctk.CTkToplevel):
    
    """
        Base class for a chat interface.
        Provides core functions to send messages, and handle incomming data 
        from the asynchronous controller.
    
        Attributes
        -------

        master : ctk
            the root tkinter object for the all aplication
        controller : BasicAsyncController
            Handles communication with the network layer and retrieve messages and 
            notifications
        message_queue : Queue
            Queue to store the messages incoming from the web
        notification_queue : Queue
            Queue to store the notifications incoming from the controller
        width : int
            canvas width
        height : int
            canvas height
        running : Bool
            Indicates whether the controller loop is ready
            
        Methods
        -------
        on_close()
            Gracefully shuts down the interface itself,the controller and the connection layer
        build_interface()
            Builds the standard layout for a chat window
        start_routines
            Start the scheduled events to keep the window in syncronous state with the
            controller
        get_notification_routine
            Non blocking routine to collect avaliable notifications from the controller  
        get_message_routine
            Non blocking routine to collect avaliable messages from the controller    
        handle_notification
            Non blocking routine to colect stored notifcations for a proper exibition on the canvas
        handle_message
            Non blocking routine to colect stored messages for a proper exibition on the canvas
        add_message_on_gui
            Insert a stored message on the tkinter canvas
        add_my_message
            Send a message to network to web and store it in the message Queue
        scroll_to_bottom
            Keep the tkinter scrolable frame aligned with the last message added to the canvas
    """

    def __init__(self , master,controller):
        super().__init__(master)
        self.master = master
        self.controller = controller
        self.message_queue = queue.Queue()
        self.notifications_queue = queue.Queue()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.destroyed = False



        self.width = 750
        self.height = 750
        self.geometry(f"{self.height}x{self.width}")
        self.running = False
        self.active_notification_gui = None


        
    def on_close(self):

        """
            Close the controller and the window itself
        """

        self.destroyed = True

        if self.running:
            self.controller.close_controller()
        try:
            self.withdraw()  
        except Exception:
            pass
        # self.destroy()
        self.running = False
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

        """
            Retrieves notifications from the controller asynchronously.

            This method schedule itself each time a new nofication is
            available in the controller, via Tkinter event loop.
        """
        
        def put_in_queue(notification):

            """
                Callback for the outer function keeping the schedule 
                operating in the right way
            """
            self.notifications_queue.put(notification)
            self.after(10 ,self.get_notification_routine)
        if not self.destroyed: 
            self.controller.get_notification(put_in_queue) 

    ## a funcao so e chamda quando um item foi retornado do controller
    ## o controlle ropera em asyncio ent pode esperar pela fila
    def get_message_routine(self):

        """
            Retrieves messages from the controller asynchronously.

            This method schedule itself each time a new message is
            available in the controller, via Tkinter event loop.
        """
        def put_in_queue(message):
            """
                Callback for the outer function keeping the schedule 
                operating in the right way
            """
            self.message_queue.put(message)
            self.after(10 ,self.get_message_routine)
        if not self.destroyed: 
            self.controller.get_web_message(put_in_queue)
    


    def handle_notification(self):

        """
            This methond schedule himself with the Tkinter
            event loop, keeping track of the notification Queue
            and operating a dynamic pop window that is responsive
            for newer notifications.
            
            If the pop window is visible  and a new nofication arrives
            it has to change dinamicaly; if the window not exist, it should 
            instanciate a new one.
        """
        def change_state(n_type):
            if n_type == NotificationType.ERROR:
                self.on_close()
            self.active_notification_gui = None


        try:
            notificaton = self.notifications_queue.get(block=False)                
            n_type = notificaton.message_type
            msg = notificaton.content

            # n_type != NotificationType.INFO: a differnt 
            # kind a notification to be added in this case in the future

            if self.active_notification_gui is not None:
                self.active_notification_gui.callback  = lambda :  change_state(n_type)
                self.master.after(2000, self.active_notification_gui.set_message, msg , n_type)
                
            else:

                self.active_notification_gui = PopUpNotificationGUI(
                    self, msg, n_type,
                    callback = lambda :  change_state(n_type))

        except queue.Empty:
            pass
        finally:  
            if not self.destroyed : self.master.after(10 , self.handle_notification)

    def handle_message(self):
        try:
            next_message = self.message_queue.get(block=False)
            self.add_message_on_gui(**next_message)
        except queue.Empty:
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