from flask import Blueprint, request, Response, jsonify
from src.ml.model_manager import ModelManager
from src.ml.definitions import ExerciseDef, ExerciseRsDef, QuestionDef, QuestionRsDef
import requests
import json
from bson.json_util import dumps 

ml = Blueprint("ml", __name__)


@ml.route("/user_assesment", methods=["POST"])
def user_assesmentd():
    user_assesment_data = request.get_json()
    user_assesment = QuestionDef(**user_assesment_data)
    model_manager = ModelManager()
    user_assesment_label = model_manager.label_student(user_assesment=user_assesment)

    return jsonify(
        {
            "student_id": user_assesment.student_id,
            "user_category": user_assesment_label,
        }
    )


@ml.route("exercise/category", methods=["POST"])
# def exercise_category(exercise: ExerciseDef) -> ExerciseRsDef:
def exercise_category():
    print("Exercise categorization")
    try:
        data = request.get_json()
        mlQuery = {
                'id': data['exercise'],
                'description': data['exercise_description'][0],
                'code':data['code']
            }
        res = requests.post('http://147.102.246.132:7462/code4code/ml/exercise_category', json=mlQuery)
        chapters = res.json()
        data["category"] = {
            "chapter": chapters['exercise_chapter'],
            "subchapter": [{
                "chapter":"",
                "subchapter": chapters['subchapters']
            }]
        }

        return Response(dumps(data), mimetype="application/json", status=201)
    except Exception as e:
        return Response(
            json.dumps({"error": f"Exercise failed to be categorized: {e}"}),
            mimetype="application/json",
            status=500,
        )
    
