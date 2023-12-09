from models import Faculty, Student, db, Location
from sqlalchemy import desc
import re
from werkzeug.security import check_password_hash, generate_password_hash
from flask import session

from static.js.utils import convertGradeToPercentage, checkStatus

def getCurrentUser():
    current_user_id = session.get('user_id')
    return Student.query.get(current_user_id)

def getStudentData(student_id):
    try:
        data_student = (
            db.session.query(Student).filter(
                Student.StudentId == student_id).first()
        )

        dict_student_data = {
                "StudentNumber": data_student.StudentNumber,
                "Name": data_student.Name,
                "PlaceOfBirth": data_student.PlaceOfBirth,
                "ResidentialAddress": data_student.ResidentialAddress,
                "Email": data_student.Email,
                "MobileNumber": data_student.MobileNumber,
                "Gender": "Male" if data_student.Gender == 1 else "Female",
            }
        return (dict_student_data)
    except Exception as e:
        # Handle the exception here, e.g., log it or return an error response
        return None
    
def updateStudentData(str_student_id, email, number, residentialAddress):
    try:
        if not re.match(r'^[\w\.-]+@[\w\.-]+$', email):
            return {"type": "email", "status": 400}

        if not re.match(r'^09\d{9}$', number):
            return {"type": "mobile", "status": 400}

        if residentialAddress is None or residentialAddress.strip() == "":
            return {"type": "residential", "status": 400}

        # Update the student data in the database
        data_student = db.session.query(Student).filter(
            Student.StudentId == str_student_id).first()
        
        if data_student:
            data_student.Email = email
            data_student.MobileNumber = number
            data_student.ResidentialAddress = residentialAddress
            db.session.commit()
                        
            return {"message": "Data updated successfully", "email": email, "number": number, "residentialAddress": residentialAddress, "status": 200}
        else:
            return {"message": "Something went wrong", "status": 404}

    except Exception as e:
        # Handle the exception here, e.g., log it or return an error response
        db.session.rollback()  # Rollback the transaction in case of an error
        return {"message": "An error occurred", "status": 500}


def updatePassword(str_student_id, password, new_password, confirm_password):
    try:
        data_student = db.session.query(Student).filter(
            Student.StudentId == str_student_id).first()

        if data_student:
            # Assuming 'password' is the hashed password stored in the database
            hashed_password = data_student.Password

            if check_password_hash(hashed_password, password):
                # If the current password matches
                new_hashed_password = generate_password_hash(
                    new_password)
                data_student.Password = new_hashed_password
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

def getLocation():
    try:
        data_location = db.session.query(Location).all()
        list_location_data = []
        if data_location:
            for location in data_location:
                location_dict = {
                    "LocationId": location.LocationId,
                    "Name": location.Name,
                }
                list_location_data.append(location_dict)
        else:
            return None
        return list_location_data
    except Exception as e:
        # Handle the exception here, e.g., log it or return an error response
        return None

def submitIncidentReport(student_id, date, time, location_id, incident_type_id, parties_involved, description):
    try:
        # Update the student data in the database
        data_student = db.session.query(Student).filter(
            Student.StudentId == student_id).first()
        
        if data_student:
            incident = IncidentReport(date=date, time=time, location_id=location_id, student_id=student_id, incident_type_id=incident_type_id, parties_involved=parties_involved, description=description)
            db.session.add(incident)
            db.session.commit()
                        
            return {"message": "Incident reported successfully", "status": 200}
        else:
            return {"message": "Something went wrong", "status": 404}

    except Exception as e:
        # Handle the exception here, e.g., log it or return an error response
        db.session.rollback()  # Rollback the transaction in case of an error
        return {"message": "An error occurred", "status": 500}

