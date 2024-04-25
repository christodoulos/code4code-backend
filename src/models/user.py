from src.config import MONGO_DBNAME
from src.enums import UserCategory, UserCourse, UserLevel
import mongoengine as me


class UserAssessment(me.EmbeddedDocument):
    course = me.EnumField(UserCourse, required=True)
    level = me.EnumField(UserLevel, required=True)

class UserEvaluationAnswer(me.EmbeddedDocument):
    question_id = me.StringField(required=True)
    # answer_text = me.StringField(required=True)
    correct = me.BooleanField(required=True)

class UserEvaluation(me.EmbeddedDocument):
    course = me.EnumField(UserCourse, required=True)
    score = me.FloatField(required=True)
    level = me.EnumField(UserLevel, required=True)
    date = me.DateTimeField(required=True)
    answers = me.ListField(me.EmbeddedDocumentField(UserEvaluationAnswer), required=True)

class UserRoles(me.EmbeddedDocument):
    category = me.EnumField(UserCategory, required=True, default=UserCategory.NONE)
    course = me.EnumField(UserCourse, required=True)
    isEnabled = me.BooleanField(required=True, default=False)
    
class User(me.Document):
    email = me.EmailField(required=True, unique=True)
    firstName = me.StringField(required=True)
    lastName = me.StringField(required=True)
    name = me.StringField(required=True)
    googleId = me.StringField(required=True)
    photoUrl = me.StringField(required=True)
    provider = me.StringField(required=True, choices=["GOOGLE"], default="GOOGLE")
    isAdmin = me.BooleanField(required=True, default=False)
    isEnabled = me.BooleanField(required=True, default=False)
    # category = me.EnumField(UserCategory, required=True, default=UserCategory.NONE)
    # category = me.ListField(me.StringField())
    assessments = me.ListField(me.EmbeddedDocumentField(UserAssessment))
    evaluations = me.ListField(me.EmbeddedDocumentField(UserEvaluation))
    roles = me.ListField(me.EmbeddedDocumentField(UserRoles))

    meta = {
        "collection": "users", 
        "db_alias": MONGO_DBNAME,
        "indexes": ["email"]
    }

    def to_mongo_dict(self):
        mongo_dict = self.to_mongo().to_dict()
        mongo_dict.pop("_id")
        return mongo_dict

    @staticmethod
    def get_user_by_google_id(googleId: str) -> "User":
        return User.objects(googleId=googleId).first()

    @staticmethod
    def get_user_by_email(email: str) -> "User":
        return User.objects(email=email).first()
