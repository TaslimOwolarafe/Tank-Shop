import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from db import stores


blp = Blueprint("stores", __name__, description="Operations on stores")


@blp.route("/store/<string:store_id>")
class Store(MethodView):
    def get(self, store_id):
        try:
            return stores[store_id]
        except KeyError:
            abort(404, "store not found.")
    def delete(self, store_id):
        try:
            del stores[store_id]
            return {'message': 'store deleted'}
        except KeyError:
            abort(404, message="store not found.")

@blp.route("/store")
class StoreList(MethodView):
    def get(self):
        return {'stores': list(stores.values())}

    def post(self):
        data = request.get_json()
        if 'name' not in data:
            abort(400, message="Bad request. 'name' is required.")
        for store in stores.values():
            if data['name'] == store["name"]:
                abort(400, message="store already exists.")
            store_id = uuid.uuid().hex
            store = {**data, "id": store_id}
            stores[store_id] = store
            return store