from flask import Blueprint, request, Response, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from src.models.exercise import Exercise, TrainingExercises
from bson.json_util import dumps, loads 
from src.enums import pyChapter, jsChapter
import json
import datetime 

exercises = Blueprint("exercises", __name__)

# Define a custom function to serialize datetime objects 
def serialize_datetime(obj): 
    if isinstance(obj, datetime.datetime): 
        return obj.isoformat() 
    raise TypeError("Type not serializable") 

@exercises.route("/one/<string:code>", methods=["GET"])
@jwt_required()
def get_exercise(code):
    try:
        exercise = Exercise.objects.get(exercise=code)
        return Response(exercise.to_json(), mimetype="application/json", status=200)
    except Exercise.DoesNotExist:
        return Response(
            json.dumps({"error": f"Exercise with code {code} does not exist"}),
            mimetype="application/json",
            status=404,
        )

#########################
### EXERCISES QUERIES ###
#########################
@exercises.route("/all/<string:type>", methods=["GET"])
@jwt_required()
def get_all_exercises_by_type(type):
    try:
        print("Get all exercises")
        if type =='all':
            courses = ['python', 'javascript']
        else:
            courses = [type]
 
        exercises = Exercise.objects.filter(type__in=courses)
        return Response(exercises.to_json(), mimetype="application/json", status=200)
    except Exercise.DoesNotExist:
        return Response(
            json.dumps({"error": f"Failed to load {type} exercises"}),
            mimetype="application/json",
            status=404,
        )

@exercises.route("/all/user/<string:email>/<string:course>", methods=["GET"])
@jwt_required()
def get_all_exercises_for_user_by_course(email,course):
    try:
        print("Get all exercises for user by course", email, course)
        exercises = Exercise.objects(author__email=email, type=course)
        return Response(exercises.to_json(), mimetype="application/json", status=200)
    except Exercise.DoesNotExist:
        return Response(
            json.dumps({"error": f"Failed to load {type} exercises for user {email}"}),
            mimetype="application/json",
            status=404,
        )


@exercises.route("/course/<string:email>/<string:course>", methods=["GET"])
@jwt_required()
def get_exercise_by_course(email,course):
    try:
        print("Get exercise for learner")
        exercises = countAllExercisesForCourse(course)
        trExercises = countAllTrainingExercisesForCourseAndUser(email, course)
        chapters = pyChapter if course=="python" else jsChapter
        for chapter in chapters:
            exercise = [x for x in exercises if x["_id"]["chapter"] == chapter ]
            training = [x for x in trExercises if x["_id"]["chapter"] == chapter ]
            if not training or exercise[0]['count'] != training[0]['count']:
                exerciseID = selectExercise(chapter)
                exercise = Exercise.objects.get(exercise=exerciseID)
                return Response(exercise.to_json(), mimetype="application/json", status=200)
    except Exercise.DoesNotExist:
        return Response(
           json.dumps({"error": f"Exercise with code {exerciseID} does not exist"}),
            mimetype="application/json",
            status=404,
        )

@exercises.route("/course/next/<string:course>/<string:difficulty>/<string:chapter>", methods=["GET"])
@jwt_required()
def get_next_exercise_by_course(course, difficulty, chapter):
    print(chapter)
    filter = {
        "type": course, 
        "difficulty": { "$in": [ "1", "2" ]},
        "category.chapter": chapter
    }

    pipeline = [
        {"$match" : filter },
        {"$sample": {"size": 1}}
    ] 
    
    try:
        print("Get next exercise for learner")
        exercises = Exercise.objects.aggregate(pipeline)
        return Response(dumps(list(exercises)), mimetype="application/json", status=200)
    except Exercise.DoesNotExist:
        return Response(
            json.dumps({"error": f"Failed to load learner's {course} next exercises"}),
            mimetype="application/json",
            status=404,
        )

@exercises.route("/chapters/<string:course>", methods=["GET"])
# @jwt_required()
def get_exercise_chapters(course):
    
    try:
        print("Get exercise chapters and number of exercises")
        chapters = Exercise.objects(type=course).distinct(field="category.chapter")
        numOfExercises = Exercise.objects(type=course).count()
        numOfExercisesByChapter = Exercise.objects.aggregate([
            { "$match": {"type":course}},
            {
                "$group" : {
                    "_id":"$category.chapter",
                    "count":{"$sum":1}
                }
            }
        ])
        numOfTrainingByChapter = TrainingExercises.objects.aggregate([
            { "$match": {"course":course}},
            {
                "$group" : {
                    "_id":"$exercises.category.chapter",
                    "count":{"$sum":1}
                }
            }
        ])
         
        data = {
            'chapters': chapters,
            'numOfExercises': numOfExercises,
            'numOfExercisesByChapter': numOfExercisesByChapter,
            'numOfTrainingByChapter': numOfTrainingByChapter
        }
        return Response(dumps(data), mimetype="application/json", status=200)
    except Exercise.DoesNotExist:
        return Response(
            json.dumps({"error": f"Failed to load exercise chapters for {course}"}),
            mimetype="application/json",
            status=404,
        )

@exercises.route("/exercise", methods=["POST"])
@jwt_required()
def set_exercise():
    try:
        print("Save exercise")
        data = request.get_json()
        exercise = Exercise(**data)
        exercise.save()
        
        return Response(exercise.to_json(), mimetype="application/json", status=201)
    except Exception as e:
        return Response(
            json.dumps({"error": f"Exercise failed to be saved: {e}"}),
            mimetype="application/json",
            status=500,
        )
    
@exercises.route("/exercise", methods=["PATCH"])
# @jwt_required()
def update_exercise():
    try: 
        print("Update Exercise")
        data = request.json
        del data["_id"]
        exercise = Exercise.objects.get(exercise=data['exercise'])
        exercise.update(**data)
        exercise.reload()
        return Response(exercise.to_json(), mimetype="application/json", status=201)   
    except Exception as e:
        return Response(
            json.dumps({"error": f"Exercise failed to update: {e}"}),
            mimetype="application/json",
            status=500,
        ) 
    
########################
### TRAINING QUERIES ###
########################

@exercises.route("/training/<string:email>", methods=["GET"])
@jwt_required()
def get_training_exercises_for_user(email):
    try:
        exercises = TrainingExercises.objects(email=email)
        return Response(exercises.to_json(), mimetype="application/json", status=200)
    except TrainingExercises.DoesNotExist:
        return Response(
            json.dumps({"error": f"Training exercises for user {email} does not exist"}),
            mimetype="application/json",
            status=404,
        )

# @exercises.route("/training/learner/<string:email>", methods=["GET"])
# @jwt_required()
# def get_learner_training_exercises(email):
#     try:
#         print("Get all training exercises for learner")
#         exercises = TrainingExercises.objects(email=email)
#         return Response(exercises.to_json(), mimetype="application/json", status=200)
#     except TrainingExercises.DoesNotExist:
#         return Response(
#             json.dumps({"error": f"Failed to load {type} training exercises for learner"}),
#             mimetype="application/json",
#             status=404,
#         )

@exercises.route("/training/count/<string:email>/<string:category>/<string:course>", methods=["GET"])
# @jwt_required()
def get_count_learner_training_exercises(email, category, course):
    try:
        print("Count all training exercises for learner by course", email, category, course)
        exercises = TrainingExercises.objects(email=email, category=category, course=course)
        return Response(exercises.to_json(), mimetype="application/json", status=200)
    except TrainingExercises.DoesNotExist:
        return Response(
            json.dumps({"error": f"Failed to load all training exercises for learner by course"}),
            mimetype="application/json",
            status=404,
        )

@exercises.route("/training", methods=["POST"])
@jwt_required()
def set_training_exercises():
    try:
        print("Training exercise to be saved")
        data = request.get_json()
        print(data)
        training = TrainingExercises(**data)
        training.save()
        return Response(training.to_json(), mimetype="application/json", status=201)
    except Exception as e:
        return Response(
            json.dumps({"error": f"Training exercise failed to be saved: {e}"}),
            mimetype="application/json",
            status=500,
        )

@exercises.route("/training", methods=["PATCH"])
@jwt_required()
def update_training_exercises():
    try:
        print("Training exercise to be updated")
        data = request.get_json()
        print(">>>",data['exercise']['exercise'], data)
        exercise = TrainingExercises.objects.get(email=data['email'], exercise__exercise=data['exercise']['exercise'])
        print(exercise)
        exercise.update(**data)
        exercise.reload()
        return Response(exercise.to_json(), mimetype="application/json", status=201)
    except Exception as e:
        return Response(
            json.dumps({"error": f"Training exercise failed to be updated: {e}"}),
            mimetype="application/json",
            status=500,
        )

@exercises.route("/training/rate", methods=["PATCH"])
@jwt_required()
def set_evaluation_for_training_exercise():
    try: 
        print("Set evaluation for training exercise")
        data = request.json
        exercise = TrainingExercises.objects.get(id=data['id']['$oid'])
        exercise.rate = data["rate"]
        exercise.save()
        return Response(json.dumps({"exercise": exercise.to_json(), "msg": "Exercise rate is updated"}), status=200)
    except Exception as e:
            return Response(
                json.dumps({"error": f"Failed set rate for training exercise"}),
                mimetype="application/json",
                status=404,
            )

def countAllExercisesForCourse(course):
    print("Count chapter exercises")
    
    pipeline = [
        {"$match" : {"type":course}},
        {
            "$group": {
                "_id": { "chapter": "$category.chapter" },
                "count": { "$sum": 1 }
            },
        }
    ]
    exercises = Exercise.objects.aggregate(pipeline)
    return list(exercises)

def countAllTrainingExercisesForCourseAndUser(email,course):
    print("Get exercise for learner")
    
    pipeline = [
        {"$match" : {
                "course":course,
                "email": email
            }
        },
        {
            "$group": {
                "_id": { "chapter": "$exercise.category.chapter" },
                "count": { "$sum": 1 }
            },
        }
    ]
    exercises = TrainingExercises.objects.aggregate(pipeline)
    return list(exercises)

def selectExercise(chapter):
    print("Get exercise for learner")
    
    pipelineExercise = [
        { "$match": {"category.chapter":chapter}},
        { "$sort": {"difficulty": 1}},
        { "$group" : {"_id" : "$category.chapter", "ids" : { "$push" : "$exercise" } } }
    ]

    pipelineTrainingExercise = [
        { "$match": {"exercise.category.chapter":chapter}},
        { "$sort": {"difficulty": 1}},
        { "$group" : {"_id" : "$exercise.category.chapter", "ids" : { "$push" : "$exercise.exercise" } } }
    ]
    exercises = list(Exercise.objects.aggregate(pipelineExercise))[0]["ids"]
    trainingExercises = list(TrainingExercises.objects.aggregate(pipelineTrainingExercise))
    
    if trainingExercises:
        trainingExercises = list(TrainingExercises.objects.aggregate(pipelineTrainingExercise))[0]["ids"]
    else: []
    exercises = [x for x in exercises if x not in trainingExercises]
    exercise = exercises[0]
    return exercise