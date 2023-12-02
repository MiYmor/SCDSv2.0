from models import Faculty, Student, db 
from sqlalchemy import desc
import re
from werkzeug.security import check_password_hash, generate_password_hash
from collections import defaultdict
import datetime

from flask import session
from static.js.utils import convertGradeToPercentage, checkStatus

from collections import defaultdict

def getCurrentUser():
    current_user_id = session.get('user_id')
    return UniversityAdmin.query.get(current_user_id)

