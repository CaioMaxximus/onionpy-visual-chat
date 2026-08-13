import os
import subprocess
from pathlib import Path
from stem.control import Controller
import time
import socket
import shutil
import docker
import secrets
from src.infrastructure import ConfigLoader

class TorServiceManager():

    """
        This class defines the methods to start and interact with the tor process.
        It allows to add , remove and configure onion servers.
    
    """

    APPLICATION_ROOT = ConfigLoader.get_application_root()
    INSTANCES_PATH = "tor_service/tor_instances"
    TOR_CONTROL_PORT = None


    global_controller = None
    config_json = None
    docker_client = None
    password= ""
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
        # data_dir = f"{folder_instace_path}/data"
        os.makedirs(folder_instace_path, exist_ok= True)

        private_key_file_name = "hs_ed25519_secret_key"
        private_key_filepath = os.path.join(folder_instace_path, private_key_file_name)

        hostname_path = os.path.join(folder_instace_path , "hostname")

        try:
            with open(private_key_filepath , "w" , encoding="utf-8") as file:
                file.write("")
        except Exception as e:
            raise RuntimeError(f"Error creating {server_name} private file : {e}")

        try:
            with open(hostname_path , "w" , encoding="utf-8") as file:
                file.write("")

        except Exception as e:
            raise RuntimeError(f"Error creating {server_name} hostname file : {e}")

        subprocess.run(["chmod", "700", folder_instace_path]) 

    @classmethod   
    def start_onion_server(cls,server_name, local_port, onion_port):

        if cls.global_controller is None:
            cls.global_controller = Controller
        onion_info = cls._start_onion_server(server_name, local_port , onion_port ,cls.global_controller)
        return onion_info

    @classmethod
    def _read_private_key_file(cls,private_key_path):


        try:
            with open(private_key_path, 'r') as key_file:
                private_key = key_file.read().strip()
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Local onion hostname adress {private_key_path} not found!")
        except Exception as e:
            raise RuntimeError("Unexpceted error during server key reading {e}")
                            
        return private_key
    
    @classmethod
    def _write_in_private_key_file(cls,private_key_path, key):

        try:
            with open(private_key_path, 'w') as key_file:
                key_file.write(key)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Local onion key adress {private_key_path} not found!")
        except Exception as e:
            raise RuntimeError("Unexpected error during server key reading {e}")

    @classmethod                        
    def _write_in_hostname_file(cls,hostname_path , hostname):

        try:
            with open(hostname_path, 'w') as host_file:
                host_file.write(hostname)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Local onion hostname adress {hostname_path} not found!")
        except Exception as e:
            raise RuntimeError("Unexpected error during server key reading {e}")

    @classmethod
    def _read_hostname_file(cls, hostname_path):

        try:
            with open(hostname_path, 'r') as host_file:
                hostname = host_file.read()
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Local onion hostname adress {hostname} not found!")
        except Exception as e:
            raise RuntimeError("Unexpceted error during server key reading {e}")
                            
        return hostname

    @classmethod
    def _create_new_onion(cls,controller,onion_port , local_port):
        with controller.from_port(port = cls.TOR_CONTROL_PORT) as ctrl:
            ctrl.authenticate(password = cls.password)

            result = ctrl.create_ephemeral_hidden_service(
                ports = {onion_port :local_port},
                key_type= "NEW",detached = True,
                await_publication=True)


        if not result:
            raise ConnectionError("Error starting onion service")
        return result

    def _start_existing_onion(cls,controller,onion_port , local_port, private_key):
        private_key = private_key.split(":")
        with controller.from_port(port = cls.TOR_CONTROL_PORT) as ctrl:
            ctrl.authenticate(password = cls.password)

            result = ctrl.create_ephemeral_hidden_service(
                ports = {onion_port :local_port},
                key_type= private_key[0]
                ,key_content = private_key[1],detached = True,
                await_publication=True)

        if not result:
            raise ConnectionError("Error starting onion service")
        return result
        
    @classmethod
    def _start_onion_server(cls,server_name, local_port, onion_port , controller):
        instance_path = f"{cls.APPLICATION_ROOT}/{cls.INSTANCES_PATH}/instance_{server_name}"
        # data_dir = f"{instance_path}/data"
        hostname_path = f"{instance_path}/hostname"
        private_key_path = f"{instance_path}/hs_ed25519_secret_key"
        private_key = cls._read_private_key_file(private_key_path)
        adrr = ""
        result = ""
        try:
            if private_key == "":
                result =cls._create_new_onion(controller,onion_port , local_port)
            else:
                result = cls._start_existing_onion(cls,controller,onion_port , local_port, private_key)

        except Exception as e:
            raise RuntimeError(f"Error connecting with the server {e}")

        adrr = f"{result.service_id}.onion"

        if private_key == "":
            complete_private_key = f"{result.private_key_type}:{result.private_key}"
            cls._write_in_private_key_file(private_key_path, complete_private_key)
            cls._write_in_hostname_file(hostname_path,adrr)

       
        return adrr

    @classmethod
    def stop_onion_server(cls,server_name):
        if not cls.check_server_exists(server_name):
            raise ValueError("Server {server_name} not found!")

        cls._stop_onion_server(server_name, cls.global_controller)

    @classmethod
    def _stop_onion_server(cls , server_name, controller): 

        instance_path = f"{cls.APPLICATION_ROOT}/{cls.INSTANCES_PATH}/instance_{server_name}"
        hostname_path = f"{instance_path}/hostname"
        hostname = cls._read_hostname_file(hostname_path).split(".")[0]

        with controller.from_port(port=cls.TOR_CONTROL_PORT) as ctrl:

            ctrl.authenticate(password = cls.password)

            res = ctrl.remove_ephemeral_hidden_service(hostname)


        
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
            
            shutil.rmtree(instance_resolved)
        except FileNotFoundError as e:
            
            raise RuntimeError(f"The server folder {path} was not found")
            
        except PermissionError as e:
            
            raise RuntimeError(f"The application is unauthorized to remove the server folder; verify your credentials.")
        except Exception as e:
            ## log here
            raise RuntimeError(f"Unexpectd error during onion server removal {e}")
 

        return



    @classmethod
    def _container_exists(cls,docker_client, container_name):

        try:
            docker_client.containers.get(container_name)
        except docker.errors.NotFound:
            return False
        except Exception as e:
            raise RuntimeError(f"Problemm trying to connect with the container {e}")
        return True


    @classmethod
    def start_tor(cls,timeout) -> None:

        cls.config_json = ConfigLoader.get_config_data()
        try:
            cls.docker_client = docker.from_env()
        except Exception  as e:
            raise RuntimeError(f"Error trying top connect to docker client {e}")

        container_name = cls.config_json["container-name"]
        img_name = cls.config_json["img-name"]
        secret_pass = secrets.token_hex(16)

        if cls._container_exists(cls.docker_client,container_name):
            print("o container ja existe")
            cls.docker_client.containers.get(container_name).remove(force = True)

        try:
            cls.docker_container =  cls.docker_client.containers.run(
            
                        image = img_name,
                        name = container_name,
                        network_mode="host",environment = {"TOR_PASSWORD" : secret_pass}
                        ,detach= True,
                        auto_remove=True
                    )
            # cls.docker_container = cls.docker_client.containers.get(container_name)
            # cls.docker_container.start(enviroment = {"TOR_PASSWORD" : secret_pass})

        except Exception as e:
            raise RuntimeError(f"Unable to start docker container {e}")

        cls.wait_for_socks(cls.config_json["port"])
        cls.TOR_CONTROL_PORT = cls.config_json["control-port"]
        cls.password = secret_pass
        
    @classmethod
    def _kill_tor(cls):
        try:
            cls.docker_container.stop()
            # cls.docker_container.wait()
        except Exception as e:
            #Log here
            pass
    
    @classmethod 
    def end_tor(cls):
        cls._kill_tor()

    @classmethod
    def check_server_exists(cls, server_name):
        return Path(f"{cls.APPLICATION_ROOT}/{cls.INSTANCES_PATH}/instance_{server_name}").is_dir()

