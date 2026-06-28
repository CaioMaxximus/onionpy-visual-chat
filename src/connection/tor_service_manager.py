import os
import subprocess
from pathlib import Path
from python_socks.sync import Proxy
# from python_socks._types import ProxyType
from stem.control import Controller
import time
import socket
import shutil
import asyncio
# from python_socks.async_.asyncio import Proxy
from python_socks import ProxyType## Temporary!

TOR_CONTROL_PORT = 9051

class TorServiceManager():

    """
        This class defines the methods to start and interact with the tor process.
        It allows to add , remove and configure onion servers.
    
    """

    APPLICATION_ROOT = os.getenv("APPLICATION_ROOT") or str(Path(__file__).resolve().parents[2])
    global_controller = None

    if not os.path.isdir(APPLICATION_ROOT):
        raise RuntimeError(f"APPLICATION_ROOT invalid: {APPLICATION_ROOT}")
    # APPLICATION_ROOT = "/home/caiomaxx/Documentos/projetos/web_chat_with_tkinter"
    INSTANCES_PATH = "tor_service/tor_instances"
    TEMPLATE_TORRC_PATH = "tor_service/files/etc/tor/torrc"
    proxy_process = None
    
    @classmethod
    def create_new_onion_server(cls, server_name ):
        if not cls.check_server_exists(server_name):
            cls._create_new_onion_server(server_name)

        else:
            raise ValueError("Server name already exists!")
    
    @classmethod
    def _create_new_onion_server(cls, server_name ):
        
        folder_instace_path = f"{cls.APPLICATION_ROOT}/{cls.INSTANCES_PATH}/instance_{server_name}"
        data_dir = f"{folder_instace_path}/data"

        os.makedirs(data_dir, exist_ok= True)
        subprocess.run(["chmod", "700", data_dir]) 

    @classmethod   
    def start_onion_server(cls,server_name, local_port, onion_port):
        if cls.global_controller is None:
            cls.global_controller = Controller
        onion_info = cls._start_onion_server(server_name, local_port , onion_port ,cls.global_controller)
        return onion_info
    
    @classmethod
    def _start_onion_server(cls,server_name, local_port, onion_port , controller):
        instance_path = f"{cls.APPLICATION_ROOT}/{cls.INSTANCES_PATH}/instance_{server_name}"
        data_dir = f"{instance_path}/data"
        hostname_path = f"{data_dir}/hostname"
        private_key_path = f"{data_dir}/hs_ed25519_secret_key"
        adrr = ""
        # id_ = None
        try:
            with controller.from_port(port = TOR_CONTROL_PORT) as ctrl:
                ctrl.authenticate()

                result = ctrl.create_hidden_service(data_dir,onion_port , target_port =local_port)

                if not result:
                    raise ConnectionError("Error starting onion service")
            with open(hostname_path, "r", encoding="utf-8") as f:
                adrr = f.read().strip()
        except FileNotFoundError as e:
            raise FileNotFoundError("Local onion hostname adress not find!")
        except Exception as e:
            raise e
                            
        return adrr

    @classmethod
    def stop_onion_server(cls,server_name):
        if not cls.check_server_exists(server_name):
            raise ValueError("Server {server_name} not found!")

        cls._stop_onion_server(server_name, cls.global_controller)

    @classmethod
    def _stop_onion_server(cls , server_name, controller): 
        instance_path = f"{cls.APPLICATION_ROOT}/{cls.INSTANCES_PATH}/instance_{server_name}"
        data_dir = f"{instance_path}/data"
        with controller.from_port(port=TOR_CONTROL_PORT) as ctrl:
            ctrl.authenticate()
            res = ctrl.remove_hidden_service(data_dir)
            print(res , "*********" * 20)
    
    # This will be used to cross-check with the sql database
    @classmethod
    def find_local_servers(cls):
        instances_path = f"{cls.APPLICATION_ROOT}/{cls.INSTANCES_PATH}"

        try:
            dirs_list = ["_".join(dir.split("_")[1:]) for dir in os.listdir(instances_path) if os.path.isdir(f"{instances_path}/{dir}")]
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Path: {instances_path} to local isntances not found, check the directories.")

        return dirs_list

    @classmethod
    def wait_for_socks(cls,port=9050, timeout=30):
        start = time.time()
        while time.time() - start < timeout:
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=10):
                    return True
            except OSError:
                time.sleep(0.3)

        raise TimeoutError("Tor SOCKS proxy Timeout.")
    
    @classmethod
    def remove_onion_service(cls,name):
        

        if not cls.check_server_exists(name):
            raise FileNotFoundError(f"Cant find {name} server directory")
        path = f"{cls.APPLICATION_ROOT}/{cls.INSTANCES_PATH}/instance_{name}"

        app_root = Path(cls.APPLICATION_ROOT).resolve()
        try:
            instance_resolved = Path(path).resolve()
            instance_resolved.relative_to(app_root)
        except Exception:
            raise ValueError("Refusing to remove directory outside APPLICATION_ROOT")

        try:
            print(instance_resolved)
            shutil.rmtree(instance_resolved)
        except Exception as e:
            raise RuntimeError(f"Failed to remove directory {app_root}") from e

        return

    @classmethod
    def start_tor(cls,timeout) -> None:

        executabel_path = f"{cls.APPLICATION_ROOT}/tor_service/files/usr/bin/tor"
        torcc_path = f"{cls.APPLICATION_ROOT}/tor_service/torrc"
        try:

            process = subprocess.Popen([f"{executabel_path}", "-f", torcc_path])
            cls.proxy_process =process  
            # cls._kill_tor()

        except Exception as e:
            cls._kill_tor()

            raise ConnectionError(
            f"Error! Trying to run tor proxy service process! check executable path: {executabel_path}"
            ) from e
        try:
            cls.wait_for_socks()
        except TimeoutError:
            cls._kill_tor()
            raise TimeoutError("Tor process dindt wake in time!")
        
        try :
            proxy = Proxy(proxy_type= ProxyType.SOCKS5,
                            host= "127.0.0.1" , port = 9050, rdns=True)
            local_socekt = proxy.connect(dest_host="8.8.8.8" , dest_port=53,timeout = timeout)
            local_socekt.close()
        except TimeoutError as e:
            cls._kill_tor()
            raise TimeoutError((f"Tor proxy was unable to connect in {timeout} seconds; please restart the application!")) from e
        except Exception as e:
            cls._kill_tor()
            raise e

    @classmethod
    def _kill_tor(cls):
        try:
            cls.proxy_process.terminate()
            cls.proxy_process.wait()
        except Exception as e:
            pass
    
    @classmethod 
    def end_tor(cls):
        cls._kill_tor()

    @classmethod
    def check_server_exists(cls, server_name):
        return Path(f"{cls.APPLICATION_ROOT}/{cls.INSTANCES_PATH}/instance_{server_name}").is_dir()

