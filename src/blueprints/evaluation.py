from flask import Blueprint, request, Response, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from src.models.evaluation import EvalQuestion
from src.models.user import User, UserEvaluation
import json
import datetime 

evalExercises = Blueprint("evaluation", __name__)

# Define a custom function to serialize datetime objects 
def serialize_datetime(obj): 
    if isinstance(obj, datetime.datetime): 
        return obj.isoformat() 
    raise TypeError("Type not serializable") 

# Evaluation Questions
@evalExercises.route("/questions/<string:course>", methods=["GET"])
@jwt_required()
def get_eval_questions(course):
    try:
        questions = EvalQuestion.objects(course=course)
        return Response(questions.to_json(), mimetype="application/json", status=200)
    except EvalQuestion.DoesNotExist:
        return Response(
            json.dumps({"error": f"Questions for course {course} does not exist"}),
            mimetype="application/json",
            status=404,
        )

@evalExercises.route("/user_evaluation", methods=["PATCH"])
@jwt_required()
def setUserEvaluations():
    user = User.get_user_by_email(get_jwt_identity())
    data = request.json
    evaluation = UserEvaluation(**data)
    user.evaluations.append(evaluation)
    # user.update(evaluations=[data])
    user.save()
    user.reload()
    user = user.to_mongo_dict()
    return Response(json.dumps({"user": user, "msg": "User profile is updated"}, default=serialize_datetime), status=200)