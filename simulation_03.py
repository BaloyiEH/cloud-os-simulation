import threading
import time
import random
import logging
import matplotlib.pyplot as plt
from collections import deque
import os

class CloudResourceManager:
    def __init__(self, total_resources=100):
        self.total_resources = total_resources
        self.available_resources = total_resources
        self.lock = threading.Lock()
        
        # Performance tracking
        self.total_requests = 0
        self.successful_requests = 0
        self.wait_times = []
        
        # Visualization setup
        self.utilization_history = deque(maxlen=30)
        self.plot_interval = 5  # Save plot every N seconds
        self.last_plot_time = time.time()
        
        # Logging setup
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(threadName)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def request_resource(self, container_id, resources_needed):
        start_time = time.time()
        with self.lock:
            self.total_requests += 1
            if self.available_resources >= resources_needed:
                self.available_resources -= resources_needed
                self.successful_requests += 1
                wait_time = time.time() - start_time
                self.wait_times.append(wait_time)
                
                # Update utilization
                utilization = (1 - self.available_resources/self.total_resources) * 100
                self.utilization_history.append(utilization)
                
                self.logger.info(f"Allocated {resources_needed} units | Remaining: {self.available_resources}")
                return True
            else:
                self.logger.warning(f"Denied {resources_needed} units | Available: {self.available_resources}")
                return False

    def release_resource(self, container_id, resources_released):
        with self.lock:
            self.available_resources += resources_released
            self.logger.info(f"Released {resources_released} units | Now available: {self.available_resources}")

    def simulate_container_workload(self, container_id):
        while True:
            resources_needed = random.randint(5, 20)
            if self.request_resource(container_id, resources_needed):
                time.sleep(random.uniform(0.1, 0.5))
                self.release_resource(container_id, resources_needed)
            time.sleep(random.uniform(0.2, 1))

    def save_utilization_plot(self):
        """Saves utilization history as PNG image"""
        plt.figure(figsize=(10, 4))
        plt.plot(list(self.utilization_history), 'b-')
        plt.title('Resource Utilization (Last 30 Steps)')
        plt.ylim(0, 100)
        plt.ylabel('Utilization %')
        plt.grid(True)
        
        # Save with timestamp
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"utilization_{timestamp}.png"
        plt.savefig(filename)
        plt.close()
        self.logger.info(f"Saved plot as {filename}")

    def performance_report(self):
        avg_wait_time = sum(self.wait_times)/len(self.wait_times) if self.wait_times else 0
        success_rate = (self.successful_requests/self.total_requests)*100 if self.total_requests else 0
        
        print("\n=== Performance Report ===")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Avg Wait Time: {avg_wait_time:.4f}s")
        print(f"Final Resources: {self.available_resources}/{self.total_resources}")
        
        # Save final plot
        self.save_utilization_plot()

def main():
    manager = CloudResourceManager()
    
    # Start container threads
    for i in range(5):
        threading.Thread(
            target=manager.simulate_container_workload,
            args=(f"Container-{i}",),
            daemon=True
        ).start()
    
    # Run simulation
    start_time = time.time()
    while time.time() - start_time < 30:  # Run for 30 seconds
        time.sleep(1)
    
    # Generate report
    manager.performance_report()

if __name__ == "__main__":
    # Clear old plot files
    for f in os.listdir():
        if f.startswith("utilization_") and f.endswith(".png"):
            os.remove(f)
    
    main()
