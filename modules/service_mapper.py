import json
import logging


class ServiceMapper:
    def __init__(self, mapping_file="data/service_mapping.json"):
        """
        Initialize the ServiceMapper.
        :param mapping_file: Path to the JSON file containing port-to-service mappings.
        """
        self.mapping_file = mapping_file
        self.logger = logging.getLogger("ServiceMapper")
        logging.basicConfig(level=logging.INFO)

        # Load service mappings
        self.service_map = self._load_service_mapping()

    def _load_service_mapping(self):
        """
        Load the service mapping file.
        :return: Dictionary of port-to-service mappings.
        """
        try:
            with open(self.mapping_file, "r") as file:
                service_map = json.load(file)
                self.logger.info(f"Loaded {len(service_map)} service mappings.")
                return service_map
        except FileNotFoundError:
            self.logger.error(f"Mapping file not found: {self.mapping_file}")
            return {}
        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding mapping file: {e}")
            return {}

    def map_services(self, open_ports):
        """
        Map open ports to known services.
        :param open_ports: List of open ports from the port scanner.
        :return: Dictionary mapping ports to known services.
        """
        mapped_services = {}
        for port in open_ports:
            service = self.service_map.get(str(port), "Unknown Service")
            mapped_services[port] = service
            self.logger.info(f"Port {port}: {service}")
        return mapped_services

    def save_mapped_services(self, mapped_services, output_file="reports/output/mapped_services.json"):
        """
        Save mapped services to a JSON file.
        :param mapped_services: Dictionary of ports and their mapped services.
        :param output_file: Path to save the JSON file.
        """
        try:
            with open(output_file, "w") as file:
                json.dump(mapped_services, file, indent=4)
            self.logger.info(f"Mapped services saved to {output_file}")
        except Exception as e:
            self.logger.error(f"Error saving mapped services: {e}")


if __name__ == "__main__":
    # Example usage
    open_ports = [22, 80, 443, 8080]

    # Initialize ServiceMapper
    mapper = ServiceMapper()

    # Map services
    mapped_services = mapper.map_services(open_ports)

    # Save results
    mapper.save_mapped_services(mapped_services)

    # Print results
    print("\nMapped Services:")
    for port, service in mapped_services.items():
        print(f"Port {port}: {service}")
