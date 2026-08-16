from customtkinter import CTkToplevel , CTkLabel, CTkButton
from src.models import Notification , NotificationType

class PopUpNotificationGUI(CTkToplevel):

    def __init__(self, master , message, notification_type, deny_option = False, disable_button = False , callback = None):
        
        super().__init__(master)
        # keep window on top of master and fixed size
        master.bind("<Configure>",self.center_position_to_midle)
        self.transient(master)
        self.resizable(False, False)
        self.title("")
        self.disable_button = disable_button
        self.message_label = CTkLabel(self, text=message)
        self.confirm_btn = CTkButton(self, text="CONFIRM", command=lambda: self.on_close(True))
        self.deny_btn = None
        if deny_option:
            self.deny_btn = CTkButton(self,text="DENY" ,
                                  command= lambda : self.on_close(False))
            self.deny_btn.pack(pady = (5, 5), side = "bottom")


        self.confirm_btn.pack(pady = (10,5) , side = "bottom")
        self.message_label.pack(pady = (12,6),side = "top")
        self.change_notification_type( notification_type)
        self.final_val = False
        self.callback = callback
        # self.protocol("WM_DELETE_WINDOW", lambda : print("suave"))

    

    def change_notification_type(self, notification_type) -> None:

        text_color = "white"
        bg = "#aec0b2"
        if notification_type is  NotificationType.SUCCESS:
            bg = "#28a745"   # verde
            text_color = "white"
        elif notification_type is NotificationType.INFO:
            bg = "#0d6efd"   # azul
            text_color = "white"
        elif notification_type is NotificationType.WARNING:
            bg = "#ffc107"   # amarelo
            text_color = "black"
        else:
            # ERROR / default
            bg = "#dc3545"   # vermelho
            text_color = "white"

        if not self.winfo_exists():
            return

        try:
            self.configure(fg_color=bg)
        except Exception:
            pass
    

        try:
            self.message_label.configure(text_color=text_color)
        except Exception:
            pass




    def center_position_to_midle(self,event):

        if self.winfo_exists():

            root_x = self.master.winfo_x()
            root_y = self.master.winfo_y()
            root_w = self.master.winfo_width()
            root_h = self.master.winfo_height()

            l_wigdet = self.winfo_width()
            l_height = self.winfo_height()

            new_x = root_x + (root_w // 2) - (l_wigdet // 2)
            new_y = root_y + (root_h // 3) - (l_height // 2)

            self.geometry(f"+{new_x}+{new_y}")


        
    def change_buttons_state(self) -> None:
        self.disable_button = not self.disable_button
    
    def set_message(self, new_msg, n_type) ->None:
        if self.winfo_exists():
            self.message_label.configure(text=new_msg)
            self.change_notification_type(n_type)

    def on_close(self,value) -> None:
        self.destroy()
        if self.callback is not None:
            self.callback()
        if not self.disable_button:
            self.final_val = value
