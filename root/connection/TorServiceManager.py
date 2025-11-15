import os
import subprocess

class TorServiceManager():

    APPLICATION_ROOT = os.getenv("APPLICATION_ROOT")
    INSTANCES_PATH = "tor_service/tor_instances"
    TEMPLATE_TORRC_PATH = "tor_service/files/etc/tor/torrc"
    
    @classmethod
    def create_new_onion_server(cls, server_name ):
        folder_instace_path = f"{cls.APPLICATION_ROOT}/{cls.INSTANCES_PATH}/instance_{server_name}"
        conf_dir = f"{folder_instace_path}/conf"
        hidden_service_dir = f"{folder_instace_path}/hidden_service"
        data_dir = f"{folder_instace_path}/data"
        torcc_path =  f"{conf_dir}/torrc"
        log_dir = f"{folder_instace_path}/logs"

        print("======")
        print(cls.APPLICATION_ROOT)
        print(conf_dir)
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

        print("Onion Server Created with sucess!!")
        

    @classmethod
    def start_onion_server(cls,server_name , server_port):
        print(server_name, "===============")
        instance_path = f"{cls.APPLICATION_ROOT}/{cls.INSTANCES_PATH}/instance_{server_name}"
        data_dir = f"{instance_path}/data"

        torcc_path = f"{instance_path}/conf/torrc"
        process = subprocess.Popen(f"{cls.APPLICATION_ROOT}/tor_service/files/usr/bin/tor -f {torcc_path}",shell= True)

        hostname_path = f"{instance_path}/hidden_service/hostname"
        adrr = ""
        # with open(hostname_path) as f:
        #     adrr = f.read().replace("\n" , "")
        return OnionConnection(adrr,"process.pid")
    
    @classmethod
    def end_onion_server(pid):
        subprocess.run(f"kill {pid}", shell= True)
    
    @classmethod
    def start_tor_proxy(cls):
        process = subprocess.Popen(f"{cls.APPLICATION_ROOT}/tor_service/files/usr/bin/tor -f {cls.APPLICATION_ROOT}/tor_service/torrc"
                                ,shell = True)
        return OnionConnection(process.pid, "process.ip")
        
    
class OnionConnection():
    def __init__(self, onion_adress , pid):
        self.onion_adress = onion_adress
        self.pid = pid