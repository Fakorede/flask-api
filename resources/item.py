from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    fresh_jwt_required,
    jwt_required,
    jwt_optional,
    get_jwt_claims,
    get_jwt_identity,
)
from models.item import ItemModel

ITEM_DELETED = "Item deleted."
ITEM_NOT_FOUND = "Item not found."
BLANK_ERROR = "'{}' cannot be left blank."
ADMIN_PRIVILEGE = "Admin privilege required."
LOGIN = "Login to learn more about these items."
NAME_EXISTS = "An item with name '{}' already exists."
ERROR_INSERTING = "An error ocurred while inserting the item."


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "price", type=float, required=True, help=BLANK_ERROR.format("price")
    )
    parser.add_argument(
        "store_id", type=int, required=True, help=BLANK_ERROR.format("store_id")
    )

    @classmethod
    @jwt_required
    def get(cls, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json(), 200
        return {"message": ITEM_NOT_FOUND}, 404

    @classmethod
    @fresh_jwt_required
    def post(cls, name: str):
        if ItemModel.find_by_name(name):
            return {"message": NAME_EXISTS.format(name)}, 400

        data = Item.parser.parse_args()

        item = ItemModel(name, **data)

        try:
            item.save_to_db()
        except:
            return {"message": ERROR_INSERTING}, 500

        return item.json(), 201

    @classmethod
    @jwt_required
    def put(cls, name: str):
        claims = get_jwt_claims()
        if not claims["is_admin"]:
            return {"message": ADMIN_PRIVILEGE}, 401

        data = Item.parser.parse_args()

        item = ItemModel.find_by_name(name)

        if item:
            item.price = data["price"]
        else:
            item = ItemModel(name, **data)

        item.save_to_db()

        return item.json(), 200

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
    @jwt_optional
    def get(cls):
        user_id = get_jwt_identity()
        items = [item.json() for item in ItemModel.find_all()]

        if user_id:
            return {"items": items}, 200
        return (
            {
                "items": [item["name"] for item in items],
                "message": LOGIN,
            },
            200,
        )
