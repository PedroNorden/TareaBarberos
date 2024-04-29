import threading
import time
from queue import Queue

def read_input_file(filename):
    with open(filename, 'r') as file:
        data = file.readlines()
        params = list(map(int, data[0].strip().split()))
        num_waiting_chairs = params[0]
        num_barbers = params[1]
        num_barber_chairs = params[2]
        customers = [list(map(int, line.strip().split())) for line in data[1:] if line.strip()]
    return num_waiting_chairs, num_barbers, num_barber_chairs, customers

class BarberShop:
    def __init__(self, num_barbers, num_waiting_chairs):
        self.barber_available = threading.Semaphore(num_barbers)  # Semaphore to manage barber availability
        self.access_chairs = threading.Lock()  # Lock to synchronize access to the waiting chairs
        self.waiting_customers = Queue(maxsize=num_waiting_chairs)  # Queue to manage waiting customers
        self.active = True

    def customer_arrives(self, customer_id):
        with self.access_chairs:
            if not self.waiting_customers.full():
                self.waiting_customers.put(customer_id)
                print(f"Cliente {customer_id} entra a la barbería y espera en la silla de espera.")
            else:
                print(f"Cliente {customer_id} llega pero se va porque todas las sillas de espera están ocupadas.")

    def barber_works(self, barber_id):
        while self.active or not self.waiting_customers.empty():
            self.barber_available.acquire()
            if not self.waiting_customers.empty():
                customer_id = self.waiting_customers.get()
                print(f"Barbero {barber_id} comienza a atender al cliente {customer_id} en la silla de barbero.")
                time.sleep(3)  # Simulating haircut time within the barber's thread
                print(f"Cliente {customer_id} se va después de ser atendido por el barbero {barber_id}.")
                self.waiting_customers.task_done()
            self.barber_available.release()

    def close_shop(self):
        self.active = False
        for _ in range(self.barber_available._value):  # Release any waiting barber
            self.barber_available.release()

def schedule_customer(shop, customer_id, delay):
    timer = threading.Timer(delay, shop.customer_arrives, [customer_id])
    timer.start()

def main():
    num_waiting_chairs, num_barbers, _, customers = read_input_file('Ejemplos/file0.data')
    shop = BarberShop(num_barbers, num_waiting_chairs)
    barbers = [threading.Thread(target=shop.barber_works, args=(i,)) for i in range(num_barbers)]
    for barber in barbers:
        barber.start()

    cumulative_delay = 0
    for i, customer in enumerate(customers):
        if len(customer) >= 1:
            cumulative_delay += customer[0]
            schedule_customer(shop, i, cumulative_delay)

    for barber in barbers:
        barber.join()

if __name__ == "__main__":
    main()
