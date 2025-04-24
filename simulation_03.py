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
        self.should_plot = True  # Control flag for plotting thread
        
        # Logging setup
        logging.basicConfig(level=logging.INFO, 
                          format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def plot_utilization(self):
        """Thread function for live plotting"""
        while self.should_plot:
            with self.lock:  # Thread-safe access to history
                history = list(self.utilization_history)
            
            self.ax.clear()
            self.ax.plot(history, 'b-')
            self.ax.set_title('Resource Utilization (Last 30 sec)')
            self.ax.set_ylim(0, 100)
            self.ax.set_xlabel('Time Steps')
            self.ax.set_ylabel('Utilization %')
            plt.pause(1)  # Update plot every second

    def request_resource(self, container_id, resources_needed):
        start_time = time.time()
        
        with self.lock:
            self.total_requests += 1
            
            if self.available_resources >= resources_needed:
                self.available_resources -= resources_needed
                self.successful_requests += 1
                
                # Update utilization history
                utilization = (1 - self.available_resources/self.total_resources) * 100
                self.utilization_history.append(utilization)
                
                wait_time = time.time() - start_time
                self.wait_times.append(wait_time)
                
                self.logger.info(f"Container {container_id} allocated {resources_needed} resources. "
                               f"Remaining: {self.available_resources}")
                return True
            else:
                self.logger.warning(f"Container {container_id} denied {resources_needed} resources. "
                                  f"Available: {self.available_resources}")
                return False

    # ... (keep your existing release_resource and simulate_container_workload methods) ...

def main():
    manager = CloudResourceManager()
    
    # Start plotting thread
    plot_thread = threading.Thread(target=manager.plot_utilization, daemon=True)
    plot_thread.start()
    
    # Create worker threads
    workers = []
    for i in range(5):
        t = threading.Thread(
            target=manager.simulate_container_workload,
            args=(f"Container-{i}",),
            daemon=True
        )
        workers.append(t)
        t.start()
    
    # Run for 30 seconds
    time.sleep(30)
    
    # Cleanup
    manager.should_plot = False  # Stop plotting thread
    plot_thread.join(timeout=1)
    manager.performance_report()

if __name__ == "__main__":
    main()
