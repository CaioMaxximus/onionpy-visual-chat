import customtkinter as ctk
from pathlib import Path
import subprocess
import sys
import zipfile

ctk.set_appearance_mode("System")  
ctk.set_default_color_theme("blue")  

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.BASE_PATH = Path(__file__).parent.resolve()
        self.title("SET-UP ONIONPY")
        self.geometry("400x300")
        self.resizable(False, False)
        self.download_daemon = False


        self.container_top = ctk.CTkFrame(self,width = 350)
        self.container_top.pack(expand = True)

        self.label_op1 = ctk.CTkLabel(self.container_top, text="Let the app use his own tor daemon through apt installation", font=("Arial", 16, "bold"),wraplength = 150)
        self.label_op1.pack(side = "left",expand = True,padx = 10)

        self.btn_deactivate = ctk.CTkButton(
            self.container_top,  width = 20,text= "",
            fg_color= "white", 
            hover_color="green",
            command=self.desativar_campo
        )
        self.btn_deactivate.pack(side = "left",expand = True)

        ## Option2

        self.container_bottom = ctk.CTkFrame(self,width = 350)
        self.container_bottom.pack(expand = True)
        
        self.label_op2 = ctk.CTkLabel(self.container_bottom, text="Use my own tor daemon", font=("Arial", 16, "bold"))
        self.label_op2.pack(side = "left",padx = 10)

        self.btn_activate =  ctk.CTkButton(
            self.container_bottom, width = 20,text= "",
            fg_color= "white", 
            hover_color="green",
            command=self.ativar_campo
        )
        self.btn_activate.pack(side = "left")

        self.entry = ctk.CTkEntry(self, width=250,placeholder_text="")
        self.entry.configure(state="disabled")
        self.entry.pack(pady=20, )


        self.confirm_btn = ctk.CTkButton(
            self, width = 50,text= "CONFIRM",
            fg_color= "green", 
            hover_color="red",
            command=self.setup_enviroment
        )
        self.confirm_btn.pack(pady = 15)


    def ativar_campo(self):

        self.entry.configure(state="normal")
        self.entry.focus()
        self.btn_activate.configure(fg_color = "green")
        self.btn_deactivate.configure(fg_color = "white")
        self.entry.configure(placeholder_text="Insert a valid tor daemon path")
        self.download_daemon = False


    def desativar_campo(self):

        self.entry.delete(0, "end")
        self.entry.configure(state="disabled")
        self.btn_activate.configure(fg_color = "white")
        self.btn_deactivate.configure(fg_color = "green")
        self.download_daemon = True
    
    def setup_enviroment(self):


        
        tor_files =  self.BASE_PATH / "tor_service/files"
        tor_instances =  self.BASE_PATH / "tor_service/tor_instances"
        tor_path = ""

        if tor_files.exists():
            ## Popup de confirmacao de remover
            pass
        else:
            tor_files.mkdir(parents= True,exist_ok=True)
        
        if self.download_daemon:
            apt_command = ["apt", "download" , "tor"]
            tor_service_folder = self.BASE_PATH / "tor_service"

            try:
                result = subprocess.run(
                    apt_command,  check= True , cwd= tor_service_folder,
                    capture_output= True , text=True
                )
            except Exception as e:
                raise e
            
            tor_daemon_file = ""
            for file in tor_service_folder.iterdir():
                if file.is_file() and file.name.startswith("tor"):
                    tor_daemon_file = file.name
                    break
            # print(tor_daemon_file)
            unpacked_daemon_path = (self.BASE_PATH / "tor_service/files")

            ## only debian for while
            unpack_command = ["dpkg" , "-x" ,( self.BASE_PATH / f"tor_service/{tor_daemon_file}" ), unpacked_daemon_path]

            try:
                subprocess.run(unpack_command , check=True)

            except Exception:
                pass
            else:

                tor_path = str(unpacked_daemon_path/ "usr/bin/tor")
                        
        else:
            tor_path = self.entry.get()

        print(tor_path)
        with open(self.BASE_PATH / "tor_daemon_path.txt", "w", encoding = "utf-8") as f:

            f.write(str(tor_path))
        tor_instances.mkdir(parents= True,exist_ok=True)

        # tor_instances = self.BASE_PATH / "tor_service/tor_instances"
        # tor_instances.mkdir()





if __name__ == "__main__":
    app = App()
    app.mainloop()
