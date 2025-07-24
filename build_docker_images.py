import subprocess
import os
import json
import platform
import time

path_to_services = "rfid_inventory/services"

def run(command):
    print(f"Running: {command}")
    subprocess.run(command, shell=True, check=True)

def load_json_file(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

# Define the services and their Dockerfile paths
services = {
    "rfid_database": "rfid_inventory/services",
    "item_tracker": "rfid_inventory/services",
    "rfid_inventory": "rfid_inventory/services",
    "portal_processor": "rfid_inventory/services",
    "tag_measurement_database": "rfid_inventory/services",
    "impinj_reader": "rfid_inventory/services",
    "gateway_reader": "proactive_sensor_gateway/services",
    "sensor_data_storage": "proactive_sensor_gateway/services",
    "viz_server": "rfid_viz/services"
}

# Services that are pulled from Docker Hub
remote_services = {
    "postgres": "postgres:latest",
}

def create_local_docker_registry(ip, port):
    # remove old registry container if it exists
    result = subprocess.run("docker rm -f registry", shell=True, stdout=subprocess.PIPE)
    # create the registry on the specified port
    print("Creating and starting registry container...")
    run(f"docker run -d -p {ip}:{port}:5000 --restart=always --name registry -e REGISTRY_STORAGE_DELETE_ENABLED=true registry:2")

def docker_login(credentials):
    print(f"🔑 Logging in to {credentials['Ip']} as {credentials['Username']}")
    process = subprocess.Popen(
        ["docker", "login", credentials["Ip"], "--username", credentials["Username"], "--password-stdin"],
        stdin=subprocess.PIPE,
    )
    process.communicate(input=credentials["Password"].encode())
    if process.returncode != 0:
        raise RuntimeError("Docker login failed.")

def build_and_push(service, dockerfile_dir, registry_url):
    image_name = f"{registry_url}/{service}"
    dockerfile_path = f"{dockerfile_dir}/{service}/Dockerfile"
    print(f"Building {service} from {dockerfile_path}")
    run(f"docker build -t {service} -f {dockerfile_path} .")
    print(f"Tagging image as {image_name}")
    run(f"docker tag {service} {image_name}")
    print(f"Pushing {image_name}")
    run(f"docker push {image_name}")

def pull_and_push_image(image_name, target_name, registry_url):
    full_target = f"{registry_url}/{target_name}"
    print(f"Pulling {image_name} from Docker Hub...")
    run(f"docker pull {image_name}")
    print(f"Tagging {image_name} as {full_target}")
    run(f"docker tag {image_name} {full_target}")
    print(f"Pushing {full_target} to local registry")
    run(f"docker push {full_target}")

if __name__ == "__main__":

    import time

    if any(arg.startswith("--") for arg in os.sys.argv):
        flagged_services = {
            service: path for service, path in services.items()
            if f"--{service}" in os.sys.argv
        }

        flagged_remote_services = {
            remote_service: image_name for remote_service, image_name in remote_services.items()
            if f"--{remote_service}" in os.sys.argv
        }
 
        if flagged_services or flagged_remote_services:
            services = flagged_services
            remote_services = flagged_remote_services 
            print(f"Building only the specified services: {list(remote_services.keys()) + list(services.keys())}")

    time.sleep(1)

    # check for --local flag
    registry_url = None    
    if "--local" in os.sys.argv:
        # Ip and Port are passed in as arguments when the --local flag is used
        # get the index of the --local flag
        local_index = os.sys.argv.index("--local")
        if len(os.sys.argv) < local_index + 3:
            print("Usage: build_docker_images.py --local <ip> <port> [--create-registry]")
            exit(1)
        ip = os.sys.argv[local_index + 1]
        port = os.sys.argv[local_index + 2]
        registry_url = f"{ip}:{port}"
        if "--create-registry" in os.sys.argv:
            create_local_docker_registry(ip, port)
    else:
        credentials = load_json_file("acr_credentials.json")
        registry_url = credentials["Ip"]
        docker_login(credentials)
    
    for service, dockerfile_dir in services.items():
        build_and_push(service, dockerfile_dir, registry_url)

    for remote_service, image_name in remote_services.items():
        target_name = remote_service.replace("_", "-")
        pull_and_push_image(remote_service, image_name, registry_url)

    print(f"All images built and pushed to Docker registry at {registry_url}")