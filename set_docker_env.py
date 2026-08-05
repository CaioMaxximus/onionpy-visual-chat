import docker
import json


def build_img():

    tag_name = "tor-daemon-onionpy-img"

    print("Starting to buld docker img")
    try:
        client = docker.from_env()
    except Exception as e:
        print(f"Error while trying to find the docker service : {e}")
        raise e
            
    try:
        print("Starting building image")

        image , logs = client.images.build(
            path  = ".",
            tag = tag_name

        )

        print("The image was build successfully")
    except docker.errors.BuildError as e:
        print(f"Error during docker build phase : {e}")
        raise e
    except Exception as e:
        print(f"There was a unexpected error {e}")
        raise e
    
def collect_valid_port_number(blacklist):

    while True:
        try:
            port_number = int(input())
            if port_number < 8000 or port_number > 10000 or port_number in blacklist:
                raise ValueError
        except Exception:
            print("iNSERT A VALID PORT NUMBER BETWEEN 8000 AND 10000")
        else:
            return port_number
        
def configure_startup_file():

    port_number = 9050
    control_number = 9051

    print("Want to change the port number for tor proxy service. (default 9050)")
    res_p = input("Enter S if you wish: ")
    if res_p.upper() == "S":
        port_number = collect_valid_port_number([])

    print("Want to change the port number for tor controll service; (default 9051)")
    res_c = input("Enter S if you wish: ")
    if res_c.upper() == "S":
        control_number = collect_valid_port_number([port_number])


    config = {
        "port" : port_number,
        "controll-port" : control_number
        }

    with open("config.json" ,"w" , encoding="utf-8") as file:
        json.dump(config, file , indent= 4)


def main():

    try:
        build_img()
    except Exception:
        return
    try:
        configure_startup_file()
    except Exception:
        return
    else:
        print("Everything ready")

if __name__ == "__main__":
    main()