from models import db, SystemAdmin
from sqlalchemy import desc
import re
from werkzeug.security import check_password_hash, generate_password_hash
from collections import defaultdict
import datetime

from flask import session

from collections import defaultdict

def getCurrentUser():
    current_user_id = session.get('user_id')
    return SystemAdmin.query.get(current_user_id)

