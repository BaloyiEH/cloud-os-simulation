import threading
import time
import random
from queue import Queue
import logging

class CloudResourceManager:
    def __init__(self, total_resources=100):
        self.total_resources = total_resources
        self.available_resources = total_resources
        self.lock = threading.Lock()
        self.resource_queue = Queue(maxsize=10)
        
        # Performance tracking
        self.total_requests = 0
        self.successful_requests = 0
        self.wait_times = []
        
        # Logging setup
        logging.basicConfig(level=logging.INFO, 
                            format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def request_resource(self, container_id, resources_needed):
        start_time = time.time()
        
        # Use a lock to ensure thread-safe resource allocation
        with self.lock:
            self.total_requests += 1
            
            # Check if resources are available
            if self.available_resources >= resources_needed:
                self.available_resources -= resources_needed
                self.successful_requests += 1
                
                wait_time = time.time() - start_time
                self.wait_times.append(wait_time)
                
                self.logger.info(f"Container {container_id} allocated {resources_needed} resources. "
                                 f"Remaining: {self.available_resources}")
                
                return True
            else:
                self.logger.warning(f"Container {container_id} could not allocate {resources_needed} resources. "
                                    f"Insufficient resources available.")
                return False

    def release_resource(self, container_id, resources_released):
        with self.lock:
            self.available_resources += resources_released
            self.logger.info(f"Container {container_id} released {resources_released} resources. "
                             f"Now available: {self.available_resources}")

    def simulate_container_workload(self, container_id):
        while True:
            # Simulate variable resource needs
            resources_needed = random.randint(5, 20)
            
            # Attempt to acquire resources
            if self.request_resource(container_id, resources_needed):
                # Simulate processing time
                time.sleep(random.uniform(0.1, 0.5))
                
                # Release resources
                self.release_resource(container_id, resources_needed)
            
            # Wait before next request
            time.sleep(random.uniform(0.2, 1))

    def performance_report(self):
        avg_wait_time = sum(self.wait_times) / len(self.wait_times) if self.wait_times else 0
        success_rate = (self.successful_requests / self.total_requests) * 100 if self.total_requests > 0 else 0
        
        print("\n--- Performance Report ---")
        print(f"Total Requests: {self.total_requests}")
        print(f"Successful Requests: {self.successful_requests}")
        print(f"Success Rate: {success_rate:.2f}%")
        print(f"Average Wait Time: {avg_wait_time:.4f} seconds")

def main():
    # Create resource manager
    resource_manager = CloudResourceManager()
    
    # Create multiple container threads
    containers = []
    for i in range(5):
        container = threading.Thread(
            target=resource_manager.simulate_container_workload, 
            args=(f"Container-{i}",), 
            daemon=True
        )
        containers.append(container)
        container.start()
    
    # Run simulation for a set duration
    time.sleep(30)
    
    # Generate performance report
    resource_manager.performance_report()

if __name__ == "__main__":
    main()
