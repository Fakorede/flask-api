from flask_restful import Resource
from flask import request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    jwt_refresh_token_required,
    get_jwt_identity,
    get_raw_jwt,
)
from marshmallow import ValidationError
from models.user import UserModel
from schemas.user import UserSchema
from blacklist import BLACKLIST
from werkzeug.security import safe_str_cmp

USER_DELETED = "User Deleted."
USER_NOT_FOUND = "User not found."
USER_EXISTS = "User already exists!"
LOGGED_OUT = "Successfully logged out."
USER_CREATED = "User created successfully."
INVALID_CREDENTIALS = "Invalid credentials."

user_schema = UserSchema()


class UserRegister(Resource):
    @classmethod
    def post(cls):
        user = user_schema.load(request.get_json())
        
        if UserModel.find_by_username(user.username):
            return {"message": USER_EXISTS}, 400

        user.save_to_db()
        return {"message": USER_CREATED}, 201


class User(Resource):
    @classmethod
    @jwt_required
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404
        return user_schema.dump(user), 200

    @classmethod
    @jwt_required
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404
        user.delete_from_db()
        return {"message": USER_DELETED}, 200


class UserLogin(Resource):
    @classmethod
    def post(cls):
        data = user_schema.load(request.get_json())

        user = UserModel.find_by_username(data.username)
        if user and safe_str_cmp(user.password, data.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {"access_token": access_token, "refresh_token": refresh_token}, 200

        return {"message": INVALID_CREDENTIALS}, 401


class UserLogout(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        jti = get_raw_jwt()["jti"]  # jti (JWT ID) is a unique id for a JWT
        BLACKLIST.add(jti)
        return {"message": LOGGED_OUT}, 200


class TokenRefresh(Resource):
    @classmethod
    @jwt_refresh_token_required
    def post(cls):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200
