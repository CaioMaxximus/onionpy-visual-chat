import docker
import json
import threading
import customtkinter as ctk

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class TorDockerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Tor Docker Setup Manager")
        self.geometry("600x650")
        self.resizable(False, False)
        self.img_name = "tor-daemon-onionpy-img"
        self.container_name = "tor-daemon-onionpy-container"

        self._build_gui()

    def _build_gui(self):
        self.title_label = ctk.CTkLabel(
            self, text="Gerenciador Tor Daemon", font=ctk.CTkFont(size=22, weight="bold")
        )
        self.title_label.pack(padx=20, pady=(20, 10))

        self.config_frame = ctk.CTkFrame(self)
        self.config_frame.pack(padx=20, pady=10, fill="x")

        self.socks_label = ctk.CTkLabel(self.config_frame, text="Port SOCKS Proxy (default 9050):")
        self.socks_label.pack(anchor="w", padx=15, pady=(10, 0))
        
        self.socks_entry = ctk.CTkEntry(self.config_frame, placeholder_text="9050")
        self.socks_entry.insert(0, "9050")
        self.socks_entry.pack(fill="x", padx=15, pady=(0, 10))

        self.control_label = ctk.CTkLabel(self.config_frame, text="Port de Controle (default 9051):")
        self.control_label.pack(anchor="w", padx=15, pady=(5, 0))

        self.control_entry = ctk.CTkEntry(self.config_frame, placeholder_text="9051")
        self.control_entry.insert(0, "9051")
        self.control_entry.pack(fill="x", padx=15, pady=(0, 15))

        self.run_button = ctk.CTkButton(
            self, text="Start configuration and build", command=self.start_process_thread, font=ctk.CTkFont(weight="bold")
        )
        self.run_button.pack(padx=20, pady=10, fill="x")

        self.log_label = ctk.CTkLabel(self, text="Logs:")
        self.log_label.pack(anchor="w", padx=20, pady=(10, 0))

        self.log_textbox = ctk.CTkTextbox(self, height=220, font=ctk.CTkFont(family="Consolas", size=12))
        self.log_textbox.pack(padx=20, pady=(5, 20), fill="both", expand=True)

    def log(self, text):
        self.log_textbox.insert("end", text + "\n")
        self.log_textbox.see("end")

    def validate_ports(self, socks_str, control_str):
        try:
            socks_port = int(socks_str)
            control_port = int(control_str)

            if not (8000 <= socks_port <= 10000) or not (8000 <= control_port <= 10000):
                self.log("❌ Erro: The port must be between 8000 and 10000.")
                return None, None

            if socks_port == control_port:
                self.log("❌ Erro: The ports cant be equal")
                return None, None

            return socks_port, control_port
        except ValueError:
            self.log("❌ Error, Insert valid numbers")
            return None, None

    def clean_previous_containers(self, client):
        try:
            container = client.containers.get(self.container_name)
            container.stop()
            container.remove()
            self.log("✔ Previous contanier removed")
        except docker.errors.NotFound:
            self.log("ℹ Not previous container found")
        except Exception as e:
            self.log(f"⚠️ Error trying to remove container: {e}")

        try:
            client.images.remove(image=self.img_name)
            self.log("✔ previous image removed")
        except docker.errors.ImageNotFound:
            self.log("ℹ Not previous Img found")
        except docker.errors.APIError as e:
            self.log(f"⚠️ Error trying to remove previous img {e}")

    def generate_torrc_file(self, port_number, control_number):
        torrc_content = f"""SocksPort 127.0.0.1:{port_number}
            ControlPort 127.0.0.1:{control_number}
            DataDirectory /var/lib/tor
            CookieAuthentication 0
            Log notice stdout
            """
        with open("torrc", "w", encoding="utf-8") as file:
            file.write(torrc_content)
        self.log("✔ 'torrc' File created successfully")

    def configure_startup_file(self, port_number, control_number):
        config = {
            "port": port_number,
            "control-port": control_number,
            "img-name": self.img_name,
            "container-name": self.container_name,
        }
        with open("config.json", "w", encoding="utf-8") as file:
            json.dump(config, file, indent=4)
        self.log("✔ 'config.json' Updated.")

    def build_img(self, client):
        self.log("⏳Starting docker ing build...")
        try:
            image, logs = client.images.build(path=".", tag=self.img_name)
            self.log(f"🚀 The image '{self.img_name}' was build successfully!")
        except docker.errors.BuildError as e:
            self.log(f"❌ Error in docker build phase: {e}")
            raise e
        except Exception as e:
            self.log(f"❌ Unexpected error: {e}")
            raise e

    def start_process_thread(self):

        self.run_button.configure(state="disabled")
        self.log_textbox.delete("1.0", "end")
        threading.Thread(target=self.run_process, daemon=True).start()

    def run_process(self):
        socks_port, control_port = self.validate_ports(
            self.socks_entry.get(), self.control_entry.get()
        )
        
        if socks_port is None or control_port is None:
            self.run_button.configure(state="normal")
            return

        try:
            client = docker.from_env()
        except Exception as e:
            self.log(f"❌ Error conecting with the docker {e}")
            self.run_button.configure(state="normal")
            return

        self.clean_previous_containers(client)
        self.configure_startup_file(socks_port, control_port)
        self.generate_torrc_file(socks_port, control_port)

        try:
            self.build_img(client)
            self.log("\n✅ Process ended!")
        except Exception:
            self.log("\n❌ The process failed during the buld.")
        finally:
            self.run_button.configure(state="normal")


if __name__ == "__main__":
    app = TorDockerApp()
    app.mainloop()