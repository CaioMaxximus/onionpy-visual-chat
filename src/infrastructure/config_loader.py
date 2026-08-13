import json
import os
from pathlib import Path

class ConfigLoader():

    _set_up_data = None
    APPLICATION_ROOT = os.getenv("APPLICATION_ROOT") or str(Path(__file__).resolve().parents[2])
    if not os.path.isdir(APPLICATION_ROOT):
            raise RuntimeError(f"APPLICATION_ROOT invalid: {APPLICATION_ROOT}")


    def _verify_loaded_data(func):

        def wrapper(*args, **kwargs):
            if ConfigLoader._set_up_data is None:
                raise ValueError("Configuration data is None. You need to call load_config_data first!")
            return func(*args, **kwargs)
        return wrapper

    # def _verify_loaded_data(func):
    #     def wrapper(*args, **kwargs):
    #         # Como é um método de classe/instância, o primeiro argumento em *args é 'cls' ou 'self'
    #         if ConfigManager._set_up_data is None:
    #             raise ValueError("Configuration data is None. You need to call load_config_data first!")
    #         return func(*args, **kwargs)
    #     return wrapper
    
    @classmethod
    def load_config_data(cls):
        print("carreguei os dados!")
        try:
            with open(f"{cls.APPLICATION_ROOT}/config.json" ,"r" , encoding="utf-8") as jfile:
                cls._set_up_data = json.load(jfile)
        except FileNotFoundError as e:
            raise RuntimeError("The setup file cannot be found, check the make install step")


    @classmethod
    @_verify_loaded_data
    def get_proxy_port_number(cls):

        return cls._set_up_data["port"]

    @classmethod
    @_verify_loaded_data
    def get_port_controll_number(cls):

        return cls._set_up_data["control-port"]

    @classmethod
    @_verify_loaded_data

    def get_container_name(cls):
        return cls._set_up_data["container-name"]

    @classmethod
    @_verify_loaded_data

    def get_image_name(cls):
        return cls._set_up_data["img-name"]

    @classmethod
    @_verify_loaded_data

    def get_config_data(cls):
        return cls._set_up_data

    @classmethod
    def get_application_root(cls):
        return cls.APPLICATION_ROOT