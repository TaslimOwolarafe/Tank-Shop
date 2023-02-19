from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, create_refresh_token, get_jwt_header, get_jwt_identity

from db import db
from models import UserModel
from schemas import UserSchema

from blocklist import BLOCKLIST

blp = Blueprint("Users", 'users', description="Operations on users")


@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, data):
        if UserModel.query.filter(UserModel.username==data['username']).first():
            abort(409, message="A user with that username already exists.")

        user = UserModel(username=data['username'], password=pbkdf2_sha256.hash(data['password']), is_admin=False)
        db.session.add(user)
        db.session.commit()
        return {'message':'user created successfully.'}, 201


@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, data):
        user = UserModel.query.filter(UserModel.username==data['username']).first()
        if user and pbkdf2_sha256.verify(data['password'], user.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(identity=user.id)
            return {'user_id': user.id, 'access_token':access_token, "refresh_token":refresh_token}

        abort(401, message="invalid credentials.")

@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        jti = get_jwt()['jti']
        BLOCKLIST.add(jti)
        return {'access_token':new_token}

@blp.route('/logout')
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        BLOCKLIST.add(jti)
        return {'message':'successfully logged out.'}

@blp.route("/user/<int:id>")
class UserDetail(MethodView):
    @blp.response(200, UserSchema)
    def get(self, id):
        user = UserModel.query.get_or_404(id)
        return user
    def delete(self, id):
        user = UserModel.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        return {'message':'user deleted.'}, 200