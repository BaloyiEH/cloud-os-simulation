import threading
import time
import random
import logging
from datetime import datetime

class CloudResourceManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.resources = 100
        # Configure logging to show thread names
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(threadName)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)

    def worker(self):
        thread_name = threading.current_thread().name
        while True:
            with self.lock:
                request = random.randint(1, 20)
                if self.resources >= request:
                    self.resources -= request
                    self.logger.info(f"Allocated {request} units | Remaining: {self.resources}")
                else:
                    self.logger.warning(f"DENIED {request} units | Available: {self.resources}")
            time.sleep(random.uniform(0.1, 0.5))

def main():
    manager = CloudResourceManager()
    threads = []
    
    # Create 5 worker threads
    for i in range(5):
        t = threading.Thread(
            target=manager.worker,
            name=f"Container-{i}",
            daemon=True
        )
        threads.append(t)
        t.start()
    
    # Run for 30 seconds
    time.sleep(30)
    print("\n=== Final Resource Count ===")
    print(f"Remaining resources: {manager.resources}")

if __name__ == "__main__":
    main()
