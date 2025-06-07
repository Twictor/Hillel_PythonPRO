from datetime import datetime, timedelta
import queue
import threading
import time
import random

OrderRequestBody = tuple[str, datetime]
DeliveryTask = tuple[str, str]  # (order_name, provider)

storage = {
    "users": [],
    "dishes": [
        {
            "id": 1,
            "name": "Salad",
            "value": 1099,
            "restaurant": "Silpo",
        },
        {
            "id": 2,
            "name": "Soda",
            "value": 199,
            "restaurant": "Silpo",
        },
        {
            "id": 3,
            "name": "Pizza",
            "value": 599,
            "restaurant": "Kvadrat",
        },
    ],
    "providers": ["uklon", "uber"],
    "active_deliveries": {"uklon": 0, "uber": 0}
}


class Scheduler:
    def __init__(self):
        self.orders: queue.Queue[OrderRequestBody] = queue.Queue()
        self.deliveries: queue.Queue[DeliveryTask] = queue.Queue()

    def process_orders(self) -> None:
        print("SCHEDULER PROCESSING...")
        while True:
            order = self.orders.get(True)
            time_to_wait = order[1] - datetime.now()
            if time_to_wait.total_seconds() > 0:
                self.orders.put(order)
                time.sleep(0.5)
            else:
                # Select delivery provider (random or optimized)
                provider = random.choice(storage["providers"])

                print(f"\n\t{order[0]} READY, SENDING TO {provider.upper()} DELIVERY")
                self.deliveries.put((order[0], provider))
                storage["active_deliveries"][provider] += 1

    def process_deliveries(self) -> None:
        print("DELIVERY PROCESSING...")
        while True:
            delivery = self.deliveries.get(True)
            order_name, provider = delivery

            print(f"\t{order_name} IS BEING DELIVERED BY {provider.upper()}...")

            if provider == "uklon":
                time.sleep(5)
            elif provider == "uber":
                time.sleep(3)

            print(f"\t{order_name} DELIVERED BY {provider.upper()}!")
            storage["active_deliveries"][provider] -= 1

    def add_order(self, order: OrderRequestBody) -> None:
        self.orders.put(order)
        print(f"\n\t{order[0]} ADDED FOR PROCESSING")


def main():
    scheduler = Scheduler()

    # Start order processing thread
    order_thread = threading.Thread(target=scheduler.process_orders, daemon=True)
    order_thread.start()

    # Start delivery processing thread
    delivery_thread = threading.Thread(target=scheduler.process_deliveries, daemon=True)
    delivery_thread.start()

    # User input:
    # A 5 (in 5 seconds)
    # B 3 (in 3 seconds)
    while True:
        order_details = input("Enter order details: ")
        data = order_details.split(" ")
        order_name = data[0]
        delay = datetime.now() + timedelta(seconds=int(data[1]))
        scheduler.add_order(order=(order_name, delay))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        raise SystemExit(0)
