import docker
import json


def build_img(tag_name, client):


    print("Starting to buld docker img")
    
            
    try:
        print("Starting building image")

        image , logs = client.images.build(
            path  = ".",
            tag = tag_name

        )
        print(f"The image {tag_name} was build successfully")
    except docker.errors.BuildError as e:
        print(f"Error during docker build phase : {e}")
        raise e
    except Exception as e:
        print(f"There was a unexpected error {e}")
        raise e

def build_container(img_name,container_name, client,port_number , control_number):
    print("entrei no buld container")
    print("Stating container creation\n")
    try:
        container = client.containers.create(

            image = img_name,
            name = container_name,
            ports = {
                '9050' : port_number,
                '9051' : control_number
            }
        )
    except Exception as e:
        print(f"There was a unexpected error {e}")
        raise e
    
    print("Container creation ending..")

    
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
        
def configure_startup_file(img_name, container_name):

    port_number = 9050
    control_number = 9051

    print("Want to change the port number for tor proxy service. (default 9050)")
    res_p = input("Enter S if you wish: ")
    if res_p.upper() == "S":
        port_number = collect_valid_port_number([])

    print("Want to change the port number for tor control service; (default 9051)")
    res_c = input("Enter S if you wish: ")
    if res_c.upper() == "S":
        control_number = collect_valid_port_number([port_number])


    config = {
        "port" : port_number,
        "control-port" : control_number,
        "img-name" : img_name,
        "container-name" : container_name
        }

    with open("config.json" ,"w" , encoding="utf-8") as file:
        json.dump(config, file , indent= 4)

    return (port_number ,control_number)


def main():

    try:
        client = docker.from_env()
    except Exception as e:
        print(f"Error while trying to find the docker service : {e}")
        return 

    img_name = "tor-daemon-onionpy-img"
    container_name = "tor-daemon-onionpy-container"

    try:
        build_img(img_name , client)
    except Exception as e:
        print(e)
        return
 
    try:
        port_number , control_number = configure_startup_file(img_name,container_name)
    except Exception as e:
        print(e)
        return

    try:
        print("build container")
        build_container(img_name , container_name,client, port_number , control_number)
    except Exception as e:
        print(e)
        return
   

if __name__ == "__main__":
    main()