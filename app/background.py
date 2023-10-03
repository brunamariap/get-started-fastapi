from datetime import datetime

def create_item_log(item_name: str, item_price: float):
    with open("item_log.txt", mode="a") as log_file:
        content = f"item name: {item_name}, item price: {item_price}, created at {datetime.now()} \n"
        log_file.write(content)