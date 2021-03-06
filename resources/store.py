from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_claims
from models.store import StoreModel
from schemas.store import StoreSchema

STORE_DELETED = "Store deleted."
STORE_NOT_FOUND = "Store not found."
STORE_EXISTS = "An store with name '{}' already exists."
ERROR_INSERTING = "An error ocurred while inserting the store."

store_schema = StoreSchema()
store_list_schema = StoreSchema(many=True)


class Store(Resource):
    @classmethod
    def get(cls, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            return store_schema.dump(store)
        return {"message": STORE_NOT_FOUND}, 404

    @classmethod
    @jwt_required
    def post(cls, name: str):
        if StoreModel.find_by_name(name):
            return {"message": STORE_EXISTS.format(name)}, 400

        store = StoreModel(name=name)

        try:
            store.save_to_db()
        except:
            return {"message": ERROR_INSERTING}, 500

        return store_schema.dump(store), 201

    @classmethod
    @jwt_required
    def delete(cls, name: str):
        store = StoreModel.find_by_name(name)
        if not store:
            return{"message": STORE_NOT_FOUND}, 404
        store.delete_from_db()
        return {"message": STORE_DELETED}, 200


class StoreList(Resource):
    @classmethod
    def get(cls):
        return {"stores": store_list_schema.dump(StoreModel.find_all())}, 200
