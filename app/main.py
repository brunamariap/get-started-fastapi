from fastapi import FastAPI
from typing import List, Optional
from uuid import UUID, uuid1
from pydantic import BaseModel


app = FastAPI()

items = dict()

class Item(BaseModel):
    name: str
    price: float


class PriceItem(BaseModel):
    price: float


class CompleteItem(BaseModel):
    id: UUID
    name: str
    price: float


@app.get("/items")
def list_items():
    return items


@app.get("/items/{item_name}")
def list_specific_item(item_name: str):
    if item_name is None or item_name not in items:
        return {"message": "invalid item"}
    else:
        return items[item_name]


@app.post("/items/create")
def create_item(item: Item):
    if item.name is None and item.price is None:
        return {"message": "invalid item"}
    elif not items.get(item.name) is None:
        return {"message": "item exists"}
    else:
        item = CompleteItem(id=uuid1(), name=item.name, price=item.price)
        items[item.name] = item
        return item


@app.patch("/items/update/{item_name}")
def update_item(item_name: str, price_item: PriceItem):
    if item_name is None or item_name not in items:
        return {"message": "invalid item"}
    else:
        if price_item is None:
            return {"message": "price is required"}

        items[item_name].price = price_item
        return {"messagem": "updated item"}


@app.delete("/items/delete/{item_name}")
def delete_item(item_name: str):
    if item_name not in items or item_name is None:
        return {"message": "invalid item"}
    else:
        del items[item_name]
        return {"message": "deleted item"}
