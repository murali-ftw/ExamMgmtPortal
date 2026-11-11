# Imports every model so other files can write: from models import User, Exam
from models.user_model import User
from models.course_model import Course
from models.exam_model import Exam, EXAM_TYPES
from models.exam_assignment_model import ExamAssignment
from models.rubric_model import Rubric
from models.slot_model import Slot
from models.booking_model import Booking
from models.evaluation_model import Evaluation, EvaluationScore
