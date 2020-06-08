from flask_restful import Resource
from flask import request
from flask_jwt_extended import (
    fresh_jwt_required,
    jwt_required,
    jwt_optional,
    get_jwt_claims,
    get_jwt_identity,
)
from marshmallow import ValidationError
from models.item import ItemModel
from schemas.item import ItemSchema


ITEM_DELETED = "Item deleted."
ITEM_NOT_FOUND = "Item not found."
ADMIN_PRIVILEGE = "Admin privilege required."
LOGIN = "Login to learn more about these items."
NAME_EXISTS = "An item with name '{}' already exists."
ERROR_INSERTING = "An error ocurred while inserting the item."

item_schema = ItemSchema()
item_list_schema = ItemSchema(many=True)


class Item(Resource):

    @classmethod
    @jwt_required
    def get(cls, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            return item_schema.dump(item), 200
        return {"message": ITEM_NOT_FOUND}, 404

    @classmethod
    @fresh_jwt_required
    def post(cls, name: str):
        if ItemModel.find_by_name(name):
            return {"message": NAME_EXISTS.format(name)}, 400

        item_json = request.get_json() # price, store_id
        item_json["name"] = name

        try:
            item = item_schema.load(item_json)
        except ValidationError as err:
            return err.messages, 400

        try:
            item.save_to_db()
        except:
            return {"message": ERROR_INSERTING}, 500

        return item_schema.dump(item), 201

    @classmethod
    @jwt_required
    def put(cls, name: str):
        claims = get_jwt_claims()
        if not claims["is_admin"]:
            return {"message": ADMIN_PRIVILEGE}, 401

        item_json = request.get_json()
        item = ItemModel.find_by_name(name)

        if item:
            item.price = item_json["price"]
        else:
            item_json["name"] = name

            try:
                item = item_schema.load(item_json)
            except ValidationError as err:
                return err.messages, 400

        item.save_to_db()

        return item_schema.dump(item), 200

    @classmethod
    @jwt_required
    def delete(cls, name: str):
        claims = get_jwt_claims()
        if not claims["is_admin"]:
            return {"message": ADMIN_PRIVILEGE}, 401

        item = ItemModel.find_by_name(name)
        if not item:
            return {"message": ITEM_NOT_FOUND}, 404
        item.delete_from_db()
        return {"message": ITEM_DELETED}, 200


class ItemList(Resource):
    @classmethod
    def get(cls):
        return {"items": item_list_schema.dump(ItemModel.find_all())}, 200
