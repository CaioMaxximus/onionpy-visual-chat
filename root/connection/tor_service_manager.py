import os
import subprocess
from pathlib import Path
import socket
from python_socks.sync import Proxy
from python_socks._types import ProxyType
from stem.control import Controller
import time
import socket

## Temporary!
TOR_CONTROL_PORT = 9051


class TorServiceManager():

    # substitua a linha original por isto
    APPLICATION_ROOT = os.getenv("APPLICATION_ROOT") or str(Path(__file__).resolve().parents[2])

    # opcional: validar existência
    if not os.path.isdir(APPLICATION_ROOT):
        raise RuntimeError(f"APPLICATION_ROOT inválido: {APPLICATION_ROOT}")
    # APPLICATION_ROOT = "/home/caiomaxx/Documentos/projetos/web_chat_with_tkinter"
    INSTANCES_PATH = "tor_service/tor_instances"
    TEMPLATE_TORRC_PATH = "tor_service/files/etc/tor/torrc"
    proxy_id = None
    
    @classmethod
    def create_new_onion_server(cls, server_name ):
        if not cls.check_server_exists(server_name):
            folder_instace_path = f"{cls.APPLICATION_ROOT}/{cls.INSTANCES_PATH}/instance_{server_name}"
            data_dir = f"{folder_instace_path}/data"

            os.makedirs(data_dir, exist_ok= True)
            subprocess.run(f"chmod 700 {data_dir}" ,shell= True,)
        
        else:
            raise ValueError("Server name already exists!")
        
    @classmethod
    def start_onion_server(cls,server_name, local_port, onion_port ):
        instance_path = f"{cls.APPLICATION_ROOT}/{cls.INSTANCES_PATH}/instance_{server_name}"
        data_dir = f"{instance_path}/data"
        hostname_path = f"{data_dir}/hostname"
        private_key_path = f"{data_dir}/hs_ed25519_secret_key"
        adrr = ""
        id_ = None
        try:
            with Controller.from_port(port = TOR_CONTROL_PORT) as controller:
                controller.authenticate()
                result = controller.create_hidden_service(data_dir,onion_port , target_port =local_port)
                if not result.hostname:
                    raise ConnectionError("Error starting onion service")
        except FileNotFoundError as e:
            raise FileNotFoundError("Local onion hostname adress not find!")
        except Exception as e:
            raise Exception from e
                            
        return OnionConnection(adrr , "id_")
    
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
            raise e


    @classmethod
    def wait_for_socks(cls,port=9050, timeout=30):
        start = time.time()
        print("esperando pelo tor")
        while time.time() - start < timeout:
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=1):
                    print("deu certo")
                    return True
            except OSError:
                time.sleep(0.3)
        


        raise TimeoutError("Tor SOCKS proxy não subiu a tempo.")

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
        except Exception as e:
            raise ConnectionError("Error! Proxy service is not working") from e
        cls.proxy_id = process.pid    
    
    @classmethod 
    def end_tor(cls):
        subprocess.run(f"kill {cls.proxy_id}", shell= True)

    @classmethod
    def check_server_exists(cls, server_name):
        return Path(f"{cls.APPLICATION_ROOT}/{cls.INSTANCES_PATH}/{server_name}").is_dir()
    

# async def send_tcp_to_onion(onion_host, port, message, timeout=30):
#     proxy = Proxy(proxy_type= ProxyType.SOCKS5,
#                             host= "127.0.0.1" , port = 9050, rdns=True)
#     sock  = await proxy.connect(dest_host = onion_host,dest_port= port,
#         )   
    
#     reader,writer = await asyncio.open_connection( 
#         sock = sock)
#     writer.write((message + "\n").encode())
#     await writer.drain()
    
class OnionConnection():
    def __init__(self, onion_adress , id):
        self.hostname = onion_adress
        self.id = id
        

if __name__ == "__main__":
    t = TorServiceManager
    # try:
    #     t.create_new_onion_server("server_test")
    # except Exception:
    #     print("suave ja existe")
    try:
        # t.start_tor(8)
        t.start_onion_server("server_test",5000,80)
        # response = asyncio.run(send_tcp_to_onion(
        # "frd2kdmrir4ovdmivlmvfxkxsho2aklyuyufkit7p5e2dp2jvy2hdvqd.onion",
        # 80, "OI!"
        # ))
        # print("conectiou")
        # time.sleep(0.3)
        print(t.find_local_servers())
        # t.end_tor()
    except Exception as e:
        raise e from Exception
    finally:
        # t.end_tor()
        pass
