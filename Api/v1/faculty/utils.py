from models import Faculty, Student, db
from sqlalchemy import desc, distinct, func
import re
from werkzeug.security import check_password_hash, generate_password_hash
import datetime

from flask import session,  jsonify
import pandas as pd

from static.js.utils import convertGradeToPercentage, checkStatus

def getCurrentUser():
    current_user_id = session.get('user_id')
    return Faculty.query.get(current_user_id)

def getFacultyData(str_teacher_id):
    try:
        data_faculty = (
            db.session.query(Faculty).filter(
                Faculty.TeacherId == str_teacher_id).first()
        )

        if data_faculty:
            dict_faculty_data = {
                "TeacherId": data_faculty.TeacherId,
                "TeacherNumber": data_faculty.TeacherNumber,
                "Name": data_faculty.Name,
                "ResidentialAddress": data_faculty.ResidentialAddress,
                "Email": data_faculty.Email,
                "MobileNumber": data_faculty.MobileNumber,
                "Gender": "Male" if data_faculty.Gender == 1 else "Female",
            }

            return (dict_faculty_data)
        else:
            return None
    except Exception as e:
        # Handle the exception here, e.g., log it or return an error response
        return None


def updateFacultyData(str_teacher_id, email, number, residential_address):
    try:
        if not re.match(r'^[\w\.-]+@[\w\.-]+$', email):
            return {"type": "email", "status": 400}

        if not re.match(r'^09\d{9}$', number):
            return {"type": "mobile", "status": 400}

        if residential_address is None or residential_address.strip() == "":
            return {"type": "residential", "status": 400}
        
        # Update the student data in the database
        data_faculty = db.session.query(Faculty).filter(
            Faculty.TeacherId == str_teacher_id).first()
        
        if data_faculty:
            data_faculty.Email = email
            data_faculty.MobileNumber = number
            data_faculty.ResidentialAddress = residential_address
            db.session.commit()

            return {"message": "Data updated successfully", "email": email, "number": number, "residential_address": residential_address, "status": 200}
        else:
            return {"message": "Something went wrong", "status": 404}

    except Exception as e:
        # Handle the exception here, e.g., log it or return an error response
        db.session.rollback()  # Rollback the transaction in case of an error
        return {"message": "An error occurred", "status": 500}


def updatePassword(str_teacher_id, password, new_password, confirm_password):
    try:
        data_faculty = db.session.query(Faculty).filter(
            Faculty.TeacherId == str_teacher_id).first()

        if data_faculty:
            # Assuming 'password' is the hashed password stored in the database
            hashed_password = data_faculty.Password

            if check_password_hash(hashed_password, password):
                # If the current password matches
                new_hashed_password = generate_password_hash(
                    new_password)
                data_faculty.Password = new_hashed_password
                db.session.commit()
                return {"message": "Password changed successfully", "status": 200}

            else:
                return {"message": "Changing Password was unsuccessful. Please try again.", "status": 400}
        else:
            return {"message": "Something went wrong", "status": 404}

    except Exception as e:
        # Handle the exception here, e.g., log it or return an error response
        db.session.rollback()  # Rollback the transaction in case of an error
        return {"message": "An error occurred", "status": 500}

        
