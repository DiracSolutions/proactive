import sys
from docker_utils.docker_image_utils import DockerImageBuilder

project_prefix = "proactive"

# Define the services and their Dockerfile paths
services = {
    "rfid_database": "rfid_inventory/services/rfid_database",
    "item_tracker": "rfid_inventory/services/item_tracker",
    "portal_processor": "rfid_inventory/services/portal_processor",
    "tag_measurement_database": "rfid_inventory/services/tag_measurement_database",
    "tag_measurement_aggregator": "rfid_inventory/services/tag_measurement_aggregator",
    "impinj_reader_v3": "rfid_inventory/services/impinj_reader",
    "impinj_reader_v4": "rfid_inventory/services/impinj_reader",
    "gateway_reader": "proactive_sensor_gateway/services/gateway_reader",
    "sensor_data_storage": "proactive_sensor_gateway/services/sensor_data_storage",
    "viz_server": "rfid_viz/services/viz_server"
}

build_args = {
    "impinj_reader_v3": ["SDK_VERSION=3"],
    "impinj_reader_v4": ["SDK_VERSION=4"]
}

if __name__ == "__main__":
    import sys

    builder = DockerImageBuilder(
        project_prefix=project_prefix,
        services=services,
        build_args=build_args,
        credentials_path = "acr_credentials.json"
    )
    builder.handle_command_line_args(sys.argv)
    builder.build()
