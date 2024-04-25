from enum import Enum


class UserCategory(Enum):
    LEARNER = "learner"
    INSTRUCTOR = "instructor"
    # INSTITUTION = "institution"
    ADMINISTRATOR = "administrator"
    NONE = "none"


class UserCourse(Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    NONE = "none"


class UserLevel(Enum):
    NOVICE = "novice"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"
    NONE = "none"

pyChapter = [
	"python string formatting",
   	"python strings",
    "python numbers",
    "python operators",
    "integer types",
	"python booleans",	 
	"python dates",
	"python dictionaries",
	"python lists",
    "basic functions",
    "built in functions",
	"python if…else",
	"python loops",
 	"lists",
	"python tuples",
   	"python while loops"    	
	"python casting",   
    "python functions",
    "python math",
   	"python sets"
]  

jsChapter = [
	"data types",
	"strings",
    "syntax variables scope"        
	"numbers",
   	"objects",
    "expressions and operators",
    "arrays",
    "control structures",
    "functions",
    "scope",
    "classes"    
]
