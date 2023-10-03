from fastapi import FastAPI, Request, Depends, BackgroundTasks, status, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from uuid import UUID, uuid1
from pydantic import BaseModel
from datetime import datetime
import json
import asyncio

from app.background import create_item_log

""" 
Middleware para reportar toda e qualquer tentativa de acessar os endpoints (registrar o máximo de dados possíveis)
Assincronismo, ter alguma endpoint que seja assíncrono, praticando o conceito
Criar uma tarefa de background, pode ser somente o log, como visto em sala de aula
Utilizar o padrão de inversão de controle por meio de injeção de dependência 
"""

app = FastAPI()

items = dict()

class ItemDependecy:
    def __init__(self, name: str, price: float) -> None:
        self.id = uuid1()
        self.name = name
        self.price = price


class Item(BaseModel):
    name: str
    price: float


def create_item_dep(name: str, price: float):
    item = ItemDependecy

class ItemWithId(BaseModel):
    id: UUID
    name: str
    price: float


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.now()
    method_name = request.method
    query_params = request.query_params
    path_params = request.path_params
    url = request.url
    with open("request_log.txt", mode="a") as reqfile:
        content = f"method: {method_name}, query param: {query_params}, path params: {path_params} received at {datetime.now()}, url: {url}\n"
        reqfile.write(content)
    response = await call_next(request)
    process_time = datetime.now() - start_time
    response.headers["X-Time-Elapsed"] = str(process_time)
    # print(response.headers)
    return response


@app.get("/items")
def list_items():
    return items


@app.post("/items/create")
def create_item(bg_task: BackgroundTasks, item : Item):
    if item.name is None and item.price is None:
        return {"message": "invalid item"}
    elif not items.get(item.name) is None:
        return {"message": "item exists"}
    else:
        item_dict = jsonable_encoder(item)
        # del item_dict['id']
        item_temp = ItemDependecy(**item_dict)
        items[item_temp.id] = item_temp
        bg_task.add_task(create_item_log, item_name=item_temp.name, item_price=item_temp.price)
        return JSONResponse(content=jsonable_encoder(item), status_code=status.HTTP_201_CREATED)


@app.put("/items/update/{item_id}")
def update_item(item_id: UUID, item = Depends(ItemDependecy)):
    if item_id is None or item_id not in items:
        return {"message": "invalid item"}
    else:
        if item is None:
            return {"message": "price is required"}

        items[item_id].name = item.name
        items[item_id].price = item.price 
        return JSONResponse({"messagem": "updated item"}, status_code=status.HTTP_200_OK)


@app.delete("/items/delete/{item_id}")
def delete_item(item_id: UUID):
    if item_id not in items or item_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
        # return {"message": "invalid item"}
    else:  
        del items[item_id]
        return JSONResponse(content={}, status_code=status.HTTP_204_NO_CONTENT)


@app.get("/items/{item_id}")
async def list_specific_item(item_id: UUID):
    if item_id is None or item_id not in items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    else:
        await asyncio.sleep(4)
        return JSONResponse(content=jsonable_encoder(items[item_id]), status_code=status.HTTP_200_OK)


# Para criar alguns itens sem que seja preciso adicionar de 1 por 1
@app.post("/items/import")
def import_items():
    with open("items.json", 'r', encoding='utf-8') as items_import:
        data = json.load(items_import)

    if data:
        for item in data:
            item = ItemDependecy(**item)
            items[item.id] = item
        return JSONResponse(content={},status_code=status.HTTP_200_OK)