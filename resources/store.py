from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_claims
from models.store import StoreModel

STORE_DELETED = "Store deleted."
STORE_NOT_FOUND = "Store not found."
STORE_EXISTS = "An store with name '{}' already exists."
ERROR_INSERTING = "An error ocurred while inserting the store."


class Store(Resource):
    def get(self, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            return store.json()
        return {"message": STORE_NOT_FOUND}, 404

    @jwt_required
    def post(self, name: str):
        if StoreModel.find_by_name(name):
            return {"message": STORE_EXISTS.format(name)}, 400

        store = StoreModel(name)

        try:
            store.save_to_db()
        except:
            return {"message": ERROR_INSERTING}, 500

        return store.json(), 201

    @jwt_required
    def delete(self, name: str):
        store = StoreModel.find_by_name(name)
        if not store:
            return{"message": STORE_NOT_FOUND}, 404
        store.delete_from_db()
        return {"message": STORE_DELETED}, 200


class StoreList(Resource):
    def get(self):
        return {"store": [store.json() for store in StoreModel.find_all()]}
