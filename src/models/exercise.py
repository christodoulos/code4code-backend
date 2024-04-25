from src.config import MONGO_DBNAME
import mongoengine as me
from src.models.user import User
from src.enums import UserCategory, UserCourse, UserLevel

class ExerciseSubchapter(me.EmbeddedDocument):
    chapter = me.StringField()
    subchapter = me.ListField(me.StringField())


class ExerciseCategory(me.EmbeddedDocument):
    chapter = me.StringField()
    subchapter = me.ListField(me.EmbeddedDocumentField(ExerciseSubchapter))


class ExerciseHint(me.EmbeddedDocument):
    text = me.StringField(required=True)
    code = me.StringField(required=True)
    penalty = me.BooleanField(required=True)


class ExerciseAuthor(me.EmbeddedDocument):
    name = me.StringField(required=True)
    email = me.StringField(required=True)


class Exercise(me.Document):
    introduction = me.ListField(me.StringField(required=True))
    subintroduction = me.ListField(me.StringField(required=True))
    exercise_description = me.ListField(me.StringField(required=True))
    category = me.EmbeddedDocumentField(ExerciseCategory)
    hints = me.ListField(me.EmbeddedDocumentField(ExerciseHint), required=True)
    author = me.EmbeddedDocumentField(ExerciseAuthor, required=True)
    exercise = me.StringField(required=True)
    type = me.StringField(required=True)
    code = me.StringField(required=True)
    output = me.ListField(me.StringField())
    difficulty = me.StringField(required=True)

    meta = {
        "collection": "exercises", 
        "db_alias": MONGO_DBNAME,
        "indexes": ["exercise"]    
    }

class TrainingExercises (me.Document):
    email = me.StringField(required=True)
    category = me.EnumField(UserCategory, required=True, default=UserCategory.NONE)
    course = me.EnumField(UserCourse, required=True)
    level = me.EnumField(UserLevel, required=True)
    answer = me.StringField(required=True)
    output = me.DynamicField(required=True)
    exercise = me.ReferenceField(Exercise) 
    user = me.ReferenceField(User)
    rate = me.StringField()

    meta = {"collection": "training", "db_alias": MONGO_DBNAME} 