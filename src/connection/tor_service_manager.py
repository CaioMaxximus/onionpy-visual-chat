import os
import subprocess
from pathlib import Path
import socket
from python_socks.sync import Proxy
from python_socks._types import ProxyType
from stem.control import Controller
import time
import socket
import shutil
import asyncio
# from python_socks.async_.asyncio import Proxy
from python_socks import ProxyType## Temporary!

TOR_CONTROL_PORT = 9051


class TorServiceManager():

    APPLICATION_ROOT = os.getenv("APPLICATION_ROOT") or str(Path(__file__).resolve().parents[2])


    if not os.path.isdir(APPLICATION_ROOT):
        raise RuntimeError(f"APPLICATION_ROOT invalid: {APPLICATION_ROOT}")
    # APPLICATION_ROOT = "/home/caiomaxx/Documentos/projetos/web_chat_with_tkinter"
    INSTANCES_PATH = "tor_service/tor_instances"
    TEMPLATE_TORRC_PATH = "tor_service/files/etc/tor/torrc"
    proxy_id = None
    
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
        subprocess.run(f"chmod 700 {data_dir}" ,shell= True,)

    @classmethod   
    def start_onion_server(cls,server_name, local_port, onion_port):
        onion_info = cls._start_onion_server(server_name, local_port , onion_port ,Controller)
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
                # if not result:
                #     raise ConnectionError("Error starting onion service")
            with open(hostname_path, "r", encoding="utf-8") as f:
                adrr = f.read().strip()
        except FileNotFoundError as e:
            raise FileNotFoundError("Local onion hostname adress not find!")
        except Exception as e:
            raise e
                            
        return adrr , ctrl

    @classmethod
    def stop_onion_server(cls,server_name):
        cls._stop_onion_server(server_name, Controller)

    @classmethod
    def _stop_onion_server(cls , server_name, controller): 
        instance_path = f"{cls.APPLICATION_ROOT}/{cls.INSTANCES_PATH}/instance_{server_name}"
        data_dir = f"{instance_path}/data"
        with controller.from_port(port=TOR_CONTROL_PORT) as ctrl:
            ctrl.authenticate()
            ctrl.remove_hidden_service(data_dir)

    
    @classmethod
    def find_local_servers(cls):
        instances_path = f"{cls.APPLICATION_ROOT}/{cls.INSTANCES_PATH}"

        try:
            dirs_list = ["_".join(dir.split("_")[1:]) for dir in os.listdir(instances_path) if os.path.isdir(f"{instances_path}/{dir}")]
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Path: {instances_path} to local isntances not found, check the directiories.")

        return dirs_list

    
    @classmethod
    def end_onion_server(cls,pid):
        try:
            subprocess.run(f"kill {pid}", shell= True)
        except Exception as e:
            raise Exception(f"Faling to kill the {pid} process")


    @classmethod
    def wait_for_socks(cls,port=9050, timeout=30):
        start = time.time()
        # print("esperando pelo tor")
        while time.time() - start < timeout:
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=10):
                    # print("tor eentrou@!")

                    return True
            except OSError:
                time.sleep(0.3)
                # print("ainda esperando pelo tor..")

        


        raise TimeoutError("Tor SOCKS proxy Timeout.")
    
    @classmethod
    def remove_onion_service(cls,name):
        

        path = f"{cls.APPLICATION_ROOT}/{cls.INSTANCES_PATH}/instance_{name}"
        if not cls.check_server_exists(name):
            raise FileNotFoundError(f"Cant find {name} server directory")
        app_root = Path(cls.APPLICATION_ROOT).resolve()
        try:
            instance_resolved = Path(path).resolve()
            instance_resolved.relative_to(app_root)
        except Exception:
            raise ValueError("Refusing to remove directory outside APPLICATION_ROOT")

        try:
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
            
        except Exception as e:
            raise RuntimeError(
            f"Error! Trying to run tor proxy service process! check executable path: {executabel_path}"
            ) from e
        cls.wait_for_socks()
        try :
            proxy = Proxy(proxy_type= ProxyType.SOCKS5,
                            host= "127.0.0.1" , port = 9050, rdns=True)
            socket = proxy.connect(dest_host="8.8.8.8" , dest_port=53,timeout = timeout)
            socket.close()
        except TimeoutError as e:
            raise RuntimeError(f"Tor proxy was unable to connect in {timeout} seconds") from e
        except Exception:
            raise
        # except Exception as e:
        #     raise ConnectionError("Error! Proxy service is not working") from e
        cls.proxy_id = process.pid    

    
    
    @classmethod 
    def end_tor(cls):
        subprocess.run(f"kill {cls.proxy_id}", shell= True)

    @classmethod
    def check_server_exists(cls, server_name):
        return Path(f"{cls.APPLICATION_ROOT}/{cls.INSTANCES_PATH}/instance_{server_name}").is_dir()

# async def start_server_connection(HOST ,PORT , message):

#     print("Inicadond a coenxao com o server onion!!")
#     proxy = Proxy(proxy_type= ProxyType.SOCKS5,
#                     host= "127.0.0.1" , port =9050, rdns=True)
#     sock  = await proxy.connect(dest_host = HOST,dest_port= PORT,
#     )   
#     reader,writer = await asyncio.open_connection( 
#                 sock = sock)
#     data = message
#     data_encoded = (data + "\n").encode()
#     writer.write(data_encoded)
#     await writer.drain()

#     resp = await reader.readline()
#     print("Server:", resp)

#     writer.close()
#     await writer.wait_closed()

    
# def is_port_open(port):
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#         return s.connect_ex(("127.0.0.1", port)) == 0

if __name__ == "__main__":
    t = TorServiceManager
    try:
        t.create_new_onion_server("server_test")
    except Exception:
        print("suave ja existe")
    
    async def exe():
        try:
            t.start_tor(8)
            await asyncio.sleep(3)
            # t.wait_for_socks()

            ad , cntrl = t.start_onion_server("server_test",5000,80, )
            # print(is_port_open(5000))
            print("inicou o server onion!!")
            host = ad
            await asyncio.sleep(4)

            # # print("conectiou")
            # # time.sleep(0.3)
            response = asyncio.create_task(start_server_connection(
            host,
            80, "OI patrao!"))
            await asyncio.sleep(25)
            # # print(t.find_local_servers())
            # t.end_tor()
            # await asyncio.sleep(5)
            t.stop_onion_server("server_test")
            await start_server_connection(
            host,80, "era pra tarr disconectado!")
        except Exception:
            raise
        finally:
            t.end_tor()
    pass

    asyncio.run(exe())
