import threading
import time
import random
from queue import Queue
import logging
import matplotlib.pyplot as plt
from collections import deque

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
        
        # Visualization setup
        self.utilization_history = deque(maxlen=30)
        self.fig, self.ax = plt.subplots()
        self.should_plot = True
        
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
                self.logger.info(f"Allocated {resources_needed} units | Remaining: {self.available_resources}")
                return True
            else:
                self.logger.warning(f"Denied {resources_needed} units | Available: {self.available_resources}")
                return False

    def release_resource(self, container_id, resources_released):
        with self.lock:
            self.available_resources += resources_released
            self.logger.info(f"Released {resources_released} units | Now available: {self.available_resources}")

    # ===== MISSING METHOD - ADD THIS =====
    def simulate_container_workload(self, container_id):
        """Thread function simulating container behavior"""
        while True:
            resources_needed = random.randint(5, 20)
            if self.request_resource(container_id, resources_needed):
                time.sleep(random.uniform(0.1, 0.5))
                self.release_resource(container_id, resources_needed)
            time.sleep(random.uniform(0.2, 1))

    def plot_utilization(self):
        """Live resource utilization plotting"""
        plt.ion()  # Interactive mode
        while self.should_plot:
            with self.lock:
                utilization = (1 - self.available_resources/self.total_resources) * 100
                self.utilization_history.append(utilization)
                self.ax.clear()
                self.ax.plot(list(self.utilization_history), 'b-')
                self.ax.set_title('Resource Utilization (Last 30 steps)')
                self.ax.set_ylim(0, 100)
                plt.pause(1)

    def performance_report(self):
        avg_wait_time = sum(self.wait_times)/len(self.wait_times) if self.wait_times else 0
        success_rate = (self.successful_requests/self.total_requests)*100 if self.total_requests else 0
        print(f"\n=== Report ===\nSuccess Rate: {success_rate:.1f}%\nAvg Wait: {avg_wait_time:.4f}s")

def main():
    manager = CloudResourceManager()
    
    # Start visualization thread
    threading.Thread(target=manager.plot_utilization, daemon=True).start()
    
    # Launch container threads
    for i in range(5):
        threading.Thread(
            target=manager.simulate_container_workload,
            args=(f"Container-{i}",),
            daemon=True
        ).start()
    
    # Run simulation
    time.sleep(30)
    manager.should_plot = False
    manager.performance_report()

if __name__ == "__main__":
    main()
