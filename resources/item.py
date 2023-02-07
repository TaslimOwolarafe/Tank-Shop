import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from db import items, stores

blp = Blueprint("Items", __name__, description="Operations on items")


@blp.route("/item/<string:item_id>")
class Item(MethodView):
    def get(self, item_id):
        try:
            return items[item_id]
        except KeyError:
            abort(404, message="item not found.")

    def delete(self, item_id):
        try:
            del items[item_id]
            return {'message': 'item deleted.'}
        except KeyError:
            abort(404, message="item not found.")

    def put(self, item_id):
        data = request.json()
        if "price" not in data or "name" not in data:
            abort(400, message="Bad request. 'price' and 'name' required")
        try:
            item = items[item_id]
            item |= data
            return item
        except KeyError:
            abort(404, message="item not found.")


@blp.route("/item")
class ItemList(MethodView):
    def get(self):
        return {'items': list(items.values())}
        
    def post(self):
        data = request.get_json()
        if (
            "price" not in data or "store_id" not in data or "name" not in data
        ):
            return {"message":"Bad request. Ensure 'price', 'store_id' and 'name' are included in JSON payload."}, 400
        
        for item in items.values():
            if (data["name"] == item["name"] and data["store_id"] == item["store_id"]):
                abort(400, message="Item already exists.")
        if data["store_id"] not in stores:
            abort(404, message="store not found.")
        item_id = uuid.uuid4().hex
        new_item = {**data, "id": item_id}
        items[item_id] = new_item
        return new_item, 201


