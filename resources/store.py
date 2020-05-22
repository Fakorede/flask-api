from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_claims
from models.store import StoreModel


class Store(Resource):

    def get(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            return store.json()
        return {"message": "Store not found"}, 404

    @jwt_required
    def post(self, name):
        if StoreModel.find_by_name(name):
            return {"message": f"An store with name '{name}' already exists."}, 400

        store = StoreModel(name)

        try:
            store.save_to_db()
        except:
            return {"message": "An error ocurred while inserting the store."}, 500

        return store.json(), 201

    @jwt_required
    def delete(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db()

        return {"message": "Store deleted"}


class StoreList(Resource):
    def get(self):
        return {"store": [store.json() for store in StoreModel.find_all()]}
