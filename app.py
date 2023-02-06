import uuid
from flask import Flask, request
from db import stores, items
from flask_smorest import abort

app = Flask(__name__)



@app.get("/store")
def get_stores():
    return {"stores": list(stores.values())}

@app.post("/store")
def create_store():
    data = request.get_json()
    store_id = uuid.uuid4().hex
    new_store = {**data, "id":store_id}
    stores[store_id] = new_store
    return new_store, 201

@app.post("/item")                                                    
def create_item():
    data = request.get_json()
    if (
        "price" not in data or "store_id" not in data or "name" not in data
    ):
        return {"message":"Bad request. Ensure 'price', 'store_id' and 'name' are included in JSON payload."}, 400
    if data["store_id"] not in stores:
        abort(404, message="store not found.")
    item_id = uuid.uuid4().hex
    new_item = {**data, "id": item_id}
    items[item_id] = new_item
    return new_item, 201

@app.get("/item/<string:item_id>/")                                                    
def get_item(item_id):
    try:
        return items[item_id]
    except KeyError:
        abort(404, message="item not found.")

@app.put("/item/<string:item_id>/")                                                    
def update_item(item_id):
    data = request.json()
    if "price" not in data or "name" not in data:
        abort(400, message="Bad request. 'price' and 'name' required")
    try:
        item = items[item_id]
        item |= data
        return item
    except KeyError:
        abort(404, message="item not found.")

@app.delete("/item/<string:item_id>/")                                                    
def delete_item(item_id):
    try:
        del items[item_id]
        return {'message': 'item deleted.'}
    except KeyError:
        abort(404, message="item not found.")


@app.get("/items")
def get_all_items():
    return {'items': list(items.values())}


@app.get("/store/<string:store_id>")                                                    
def get_store(store_id):
    try:
        return stores[store_id]
    except KeyError:
        abort(404, "store not found.")


@app.delete("/store/<string:store_id>")                                                    
def delete_store(store_id):
    try:
        del stores[store_id]
        return {'message': 'store deleted'}
    except KeyError:
        abort(404, "store not found.")
    