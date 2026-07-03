import customtkinter as ctk
from pathlib import Path
import subprocess
import sys
import zipfile
import threading

ctk.set_appearance_mode("System")  
ctk.set_default_color_theme("blue")  

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.BASE_PATH = Path(__file__).parent.resolve()
        self.title("SET-UP ONIONPY")
        self.geometry("400x400")
        self.resizable(False, False)
        self.download_daemon = False
        self.status_queue = []
        self.not_runnig  = True


        self.container_top = ctk.CTkFrame(self,width = 350)
        self.container_top.pack(expand = True)

        self.label_op1 = ctk.CTkLabel(self.container_top, text="Let the app use his own tor daemon through apt installation", font=("Arial", 16, "bold"),wraplength = 150)
        self.label_op1.pack(side = "left",expand = True,padx = 10)

        self.btn_deactivate = ctk.CTkButton(
            self.container_top,  width = 20,text= "",
            fg_color= "white", 
            hover_color="green",
            command=self.deactivate_field
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
            command=self.activate_field
        )
        self.btn_activate.pack(side = "left")

        self.entry = ctk.CTkEntry(self, width=250,placeholder_text="")
        self.entry.configure(state="disabled")
        self.entry.pack(pady=20, )


        self.confirm_btn = ctk.CTkButton(
            self, width = 50,text= "CONFIRM",
            fg_color= "green", 
            hover_color="red",
            command=self.start_setup_enviroment
        )
        self.confirm_btn.pack(pady = 15)


        self.info_field = ctk.CTkLabel(self, wraplength=280, height=50,text="")
        self.info_field.pack(expand = True)

    def set_status_text(self, text):
        def schedule():
            if not self.status_queue:
                self.not_runnig = True
                return
            # print("chamei o schedule")

            new_sattus = self.status_queue.pop(0)
            self.info_field.configure(text = new_sattus)
            self.after(900 , schedule)
        if self.not_runnig:
            self.status_queue.append(text)
            self.not_runnig = False
            schedule()        
        else:
            self.status_queue.append(text)
        

    def activate_field(self):

        self.entry.configure(state="normal")
        self.entry.focus()
        self.btn_activate.configure(fg_color = "green")
        self.btn_deactivate.configure(fg_color = "white")
        self.entry.configure(placeholder_text="Insert a valid tor daemon path")
        self.download_daemon = False


    def deactivate_field(self):

        self.entry.delete(0, "end")
        self.entry.configure(state="disabled")
        self.btn_activate.configure(fg_color = "white")
        self.btn_deactivate.configure(fg_color = "green")
        self.download_daemon = True

    def start_setup_enviroment(self):

        self.deactivate_all_fields()
        thread = threading.Thread(target=self.setup_enviroment)
        thread.start()

    def deactivate_all_fields(self):
        self.entry.configure(state="disabled")
        self.btn_activate.configure(state="disabled")
        self.btn_deactivate.configure(state="disabled")




    def setup_enviroment(self):


        tor_files =  self.BASE_PATH / "tor_service/files"
        tor_instances =  self.BASE_PATH / "tor_service/tor_instances"
        tor_path = ""
        self.set_status_text("Starting setup!")
        if tor_files.exists():
            ## Popup de confirmacao de remover
            pass
        else:
            tor_files.mkdir(parents= True,exist_ok=True)
        
        if self.download_daemon:
            self.set_status_text("Downloading tor daemon")

            apt_command = ["apt", "download" , "tor"]
            tor_service_folder = self.BASE_PATH / "tor_service"

            try:
                result = subprocess.run(
                    apt_command,  check= True , cwd= tor_service_folder,
                    capture_output= True , text=True
                )
            except Exception as e:
                raise e
            else:
                self.set_status_text("Tor daemon download sucecced")

            
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
                self.set_status_text("Tor daemon unpack sucecced")
                tor_path = str(unpacked_daemon_path/ "usr/bin/tor")
                        
        else:
            tor_path = self.entry.get()

        print(tor_path)
        with open(self.BASE_PATH / "tor_daemon_path.txt", "w", encoding = "utf-8") as f:

            f.write(str(tor_path))

        self.set_status_text("Tor file path created successfully")

        config = [
        "SocksPort 9050\n",
        "ControlPort 9051\n"
        ]

        with open(self.BASE_PATH / "tor_service/torrc", "w", encoding = "utf-8") as f:

            f.writelines(config)

        self.set_status_text("Torcc file created")

        tor_instances.mkdir(parents= True,exist_ok=True)
        self.set_status_text("Tor instances folder creation sucecced")
        self.set_status_text("Everything Done")



        # tor_instances = self.BASE_PATH / "tor_service/tor_instances"
        # tor_instances.mkdir()





if __name__ == "__main__":
    app = App()
    app.mainloop()
