import os
import subprocess
from pathlib import Path
import socket
import asyncio
from python_socks.sync import Proxy
from python_socks._types import ProxyType
import signal


class TorServiceManager():

    APPLICATION_ROOT = os.getenv("APPLICATION_ROOT")
    INSTANCES_PATH = "tor_service/tor_instances"
    TEMPLATE_TORRC_PATH = "tor_service/files/etc/tor/torrc"
    proxy_id = None
    
    @classmethod
    def create_new_onion_server(cls, server_name ):
        if not cls.check_server_exists(server_name):
            folder_instace_path = f"{cls.APPLICATION_ROOT}/{cls.INSTANCES_PATH}/instance_{server_name}"
            conf_dir = f"{folder_instace_path}/conf"
            hidden_service_dir = f"{folder_instace_path}/hidden_service"
            data_dir = f"{folder_instace_path}/data"
            torcc_path =  f"{conf_dir}/torrc"
            log_dir = f"{folder_instace_path}/logs"

            os.makedirs(conf_dir, exist_ok= True)
            os.makedirs(hidden_service_dir, exist_ok= True)
            os.makedirs(data_dir, exist_ok= True)
            os.makedirs(log_dir)
            subprocess.run(["cp", f"{cls.APPLICATION_ROOT}/{cls.TEMPLATE_TORRC_PATH}",torcc_path], check=True)
            subprocess.run(f"chmod 700 {hidden_service_dir}" ,shell= True)
            with open(torcc_path , "a") as file:
                file.write(f"HiddenServiceDir {hidden_service_dir}\n")
                file.write(f"HiddenServicePort 80 127.0.0.1:{8080}\n")
                file.write(f"DataDirectory {data_dir}\n")
                file.write(f"SocksPort 0\n")
                file.write(f"Log notice file {log_dir}/tor_notice.log\nLog err file {log_dir}/tor_error.log")
        else:
            raise ValueError("Server name already exists!")
          
        
    @classmethod
    def start_onion_server(cls,server_name, timeout = 10 ):
        instance_path = f"{cls.APPLICATION_ROOT}/{cls.INSTANCES_PATH}/{server_name}"
        data_dir = f"{instance_path}/data"
        torcc_path = f"{instance_path}/conf/torrc"
        hostname_path = f"{instance_path}/hidden_service/hostname"
        adrr = ""
        process = None
        try :
            
            process = subprocess.Popen(f"{cls.APPLICATION_ROOT}/tor_service/files/usr/bin/tor -f {torcc_path}",shell= True)
            adrr = ()
        except Exception as e:
            raise e
        try:
            with open(hostname_path) as f:
                adrr = f.read().replace("\n" , "").split(":")
        except FileNotFoundError as e:
            raise FileNotFoundError("Local onion hostname adress not find!")
        except Exception as e:
            raise e
        try:
            cls.check_server_conection(adrr[0] , adrr[1], timeout= timeout)
        except Exception as e:
            raise e
        
        return OnionConnection(adrr,process.pid)

    
    @classmethod
    def find_local_servers(cls):
        instances_path = f"{cls.APPLICATION_ROOT}/{cls.INSTANCES_PATH}"

        try:
            dirs_list = [dir for dir in os.listdir(instances_path) if os.path.isdir(f"{instances_path}/{dir}")]
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
    async def start_tor_proxy(cls,timeout) -> None:

        executabel_path = f"{cls.APPLICATION_ROOT}/tor_service/files/usr/bin/tor"
        torcc_path = f"{cls.APPLICATION_ROOT}/tor_service/torrc"
        try:

            process = subprocess.Popen([f"{executabel_path}", "-f", torcc_path])
            
        except Exception as e:
            raise RuntimeError(
            f"Error! Trying to run tor proxy service process! check executable path: {executabel_path}"
            ) from e
        
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
        
        # return OnionConnection(process.pid, "process.ip")
    

    @classmethod
    def check_server_exists(cls, server_name):
        return Path(f"{cls.APPLICATION_ROOT}/{cls.INSTANCES_PATH}/{server_name}").is_dir()
    
    @classmethod
    def check_server_conection(cls,onion_adress, port , timeout):
       
        try:
            proxy = Proxy(proxy_type= ProxyType.SOCKS5,
                            host= "127.0.0.1" , port = 9050, rdns=True)
            sock  = proxy.connect(dest_host = onion_adress,dest_port= port,timeout = timeout)
            sock.close()
        except Exception as e:
            raise e
        
    @classmethod
    def stop_tor(cls):
        if cls.proxy_id is None:
                return

        try:
            os.kill(cls.proxy_id, signal.SIGTERM)
        except ProcessLookupError:
            pass  # processo já morreu
        except Exception as e:
            raise RuntimeError(f"Erro ao encerrar Tor PID {cls.proxy_id}: {e}")
    
class OnionConnection():
    def __init__(self, onion_adress , pid):
        self.onion_adress = onion_adress
        self.pid = pid