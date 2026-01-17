from customtkinter import CTkToplevel , CTkLabel, CTkButton
from models import Notification , NotificationType

class PopUpNotificationGUI(CTkToplevel):

    def __init__(self, master , message, notification_type, deny_option = False, disable_button = False , callback = None):
        
        super().__init__(master)
        # keep window on top of master and fixed size
        self.transient(master)
        self.resizable(False, False)

        
        self.disable_button = disable_button
        self.message_label = CTkLabel(self, text=message)
        self.confirm_btn = CTkButton(self, text="CONFIRM", command=lambda: self.close(True))
        self.deny_btn = None
        if deny_option:
            self.deny_btn = CTkButton(self,text="DENY" ,
                                  command= lambda : self.close(False))
            self.deny_btn.pack(pady = (5, 5), side = "bottom")


        self.confirm_btn.pack(pady = (10,5) , side = "bottom")
        self.message_label.pack(pady = (12,6),side = "top")
        self.change_notification_type( notification_type)
        self.final_val = False
        self.callback = callback

    

    def change_notification_type(self, notification_type):
        if notification_type == NotificationType.SUCCESS:
            bg = "#28a745"   # verde
            text_color = "white"
        # elif notification_type == NotificationType.INFO:
        #     bg = "#0d6efd"   # azul
        #     text_color = "white"
        elif notification_type == NotificationType.WARNING:
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
            self.configure(bg=bg)

        try:
            self.message_label.configure(fg_color=bg, text_color=text_color)
        except Exception:
            try:
                self.message_label.configure(text_color=text_color)
            except Exception:
                pass

        
    def change_buttons_state(self) -> None:
        self.disable_button = not self.disable_button
    
    def set_message(self, new_msg, n_type) ->None:
        if self.winfo_exists():
            self.message_label.configure(text=new_msg)
            self.change_notification_type(n_type)

    def close(self,value) -> None:
        if self.callback is not None:
            self.callback()
        if not self.disable_button:
            self.final_val = value
            self.destroy()