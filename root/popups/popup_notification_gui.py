from customtkinter import CTkToplevel , CTkLabel, CTkButton

class PopUpNotificationGUI(CTkToplevel):

    def __init__(self, master , message, deny_option = False, disable_button = False , callback = None):
        
        super().__init__(master)
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
        self.final_val = False
        self.callback = callback
        
    def change_buttons_state(self) -> None:
        self.disable_button = not self.disable_button
    
    def set_message(self, new_msg) ->None:
        self.message_label.configure(text=new_msg)

    def close(self,value) -> None:
        if self.callback is not None:
            self.callback()
        if not self.disable_button:
            self.final_val = value
            self.destroy()