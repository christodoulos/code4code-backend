from flask import Blueprint, request, Response
from google.oauth2 import id_token
from google.auth.transport import requests
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from src.config import GOOGLE_AUDIENCE
from src.models.user import User
import json


auth = Blueprint("auth", __name__)


@auth.route("/google-auth", methods=["POST"])
def google_auth():
    idToken = request.json["idToken"]
    try:
        id_info = id_token.verify_oauth2_token(idToken, requests.Request(), GOOGLE_AUDIENCE)
    except Exception as e:
        print(e)
        return Response({"error": "Invalid user"}, status=401)

    user = User.get_user_by_google_id(id_info["sub"])

    if not user:
        user = User(
            email=id_info["email"],
            firstName=id_info["given_name"],
            lastName=id_info["family_name"],
            name=id_info["name"],
            googleId=id_info["sub"],
            photoUrl=id_info["picture"],
        )
        user.save()
    else:
        user.update(
            email=id_info["email"],
            firstName=id_info["given_name"],
            lastName=id_info["family_name"],
            name=id_info["name"],
            photoUrl=id_info["picture"],
        )

    additional_claims = {"isAdmin": user.isAdmin, "isEnabled": user.isEnabled}
    access_token = create_access_token(identity=user.email, additional_claims=additional_claims)

    return Response(json.dumps({"accessToken": access_token}), status=200)


@auth.route("/profile", methods=["PATCH"])
@jwt_required()
def update_profile():
    user = User.get_user_by_email(get_jwt_identity())
    data = request.json
    user.update(**data, isEnabled=True)
    user.reload()
    user = user.to_mongo_dict()
    return Response(json.dumps({"user": user, "msg": "User profile is updated"}), status=200)


@auth.route("/user", methods=["GET"])
@jwt_required()
def get_user():
    user = User.get_user_by_email(get_jwt_identity())
    return Response(json.dumps(user.to_mongo_dict()), status=200)
