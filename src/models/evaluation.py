from src.config import MONGO_DBNAME
from src.enums import UserCourse, UserLevel
import mongoengine as me
from src.models.exercise import Exercise
from src.models.user import User


class Answer(me.EmbeddedDocument):
    text = me.StringField(required=True)
    correct = me.BooleanField(required=True)


class EvalQuestion(me.Document):
    question = me.StringField(required=True)
    answers = me.ListField(me.EmbeddedDocumentField(Answer), required=True)
    course = me.EnumField(UserCourse, required=True)
    level = me.EnumField(UserLevel, required=True)
    gravity = me.FloatField(required=True)

    meta = {"collection": "eval-questions", "db_alias": MONGO_DBNAME}