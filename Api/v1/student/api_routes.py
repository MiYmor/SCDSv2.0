# api/api_routes.py
from flask import jsonify
from flask import Blueprint, jsonify, request, redirect, url_for, flash, session, render_template
from sqlalchemy import desc
from werkzeug.security import check_password_hash
from models import Student, db, IncidentReport, Location, IncidentType , ViolationForm
import os

from decorators.auth_decorators import role_required

# FUNCTIONS IMPORT
from .utils import getStudentData, updateStudentData, updatePassword, getCurrentUser, getLocation
from werkzeug.security import generate_password_hash

from flask_mail import Message
from mail import mail  # Import mail from the mail.py module
import secrets
from datetime import datetime, timedelta
student_api_base_url = os.getenv("STUDENT_API_BASE_URL")
student_api = Blueprint('student_api', __name__)
# from app import create_app
# Api/v1/student/api_routes.py

# ===================================================
# TESTING AREA
# Step 4: Handle the form submission for requesting a password reset email
@student_api.route('/reset_password', methods=['POST'])
def forgotPassword():
    print("HEREIN RESET")
    data = request.get_json()
    email = data.get('email')
    print('email: ', email)

    # Check if email exists in the database
    student = Student.query.filter_by(Email=email).first()

    if student:
        # Generate a secure token
        token = secrets.token_hex(16)

        # Save the token and its expiration time in the database
        student.Token = token
        student.TokenExpiration = datetime.now() + timedelta(minutes=30)
        db.session.commit()

        # Send the reset email
        msg = Message('Password Reset Request', sender='your_email@example.com', recipients=[email])
        msg.body = f"Please click the following link to reset your password: {url_for('student_api.resetPasswordConfirm', token=token, _external=True)}"
        mail.send(msg)
        flash('An email with instructions to reset your password has been sent.', 'info')
        return jsonify({'message': 'An email with instructions to reset your password has been sent to email.'}),200
    else:
        return jsonify({'message': 'Invalid email'}), 400


# Step 6: Create a route to render the password reset confirmation form
@student_api.route('/reset_password_confirm/<token>', methods=['GET'])
def resetPasswordConfirm(token):
    print("GETTING")
    # Check if the token is valid and not expired
    student = Student.query.filter_by(Token=token).first()
    print("STUDENT EXIST")
    if student and student.TokenExpiration > datetime.now():
        print("STUDENT VALID")
        return render_template('student/reset_password_confirm.html', token=token, student_api_base_url=student_api_base_url)
    else:
        print("STUDENT TOKEN EXPIRED")
        flash('Invalid or expired token.', 'danger')
        return render_template('404.html')
# student_api.py (continued)


# Step 8: Handle the form submission for resetting the password
@student_api.route('/reset_password_confirm/<token>', methods=['POST'])
def resetPassword(token):
    data = request.get_json()
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')
    
    if new_password != confirm_password:
        return jsonify({'message': 'Passwords do not match', 'status': 400})
    else: 
        # Check if the token is valid and not expired
        student = Student.query.filter_by(Token=token).first()

        if student and student.TokenExpiration > datetime.now():
            # Update the password for the user in the database
            student.Password = generate_password_hash(new_password)

            # Clear the token and expiration
            student.Token = None
            student.TokenExpiration = None

            db.session.commit()

            return jsonify({'message': 'Password reset successfully', 'status': 200})
        else:
            return jsonify({'message': 'Invalid or expired token', 'status': 400})



# ===================================================
# Student User Log in
@student_api.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        print("STUDENT")
        email = request.form['email']
        password = request.form['password']
        # create_app.sayHello()
        student = Student.query.filter_by(Email=email).first()
        if student and check_password_hash(student.Password, password):
            # Successfully authenticated
            # access_token = create_access_token(identity=student.StudentId)
            # refresh_token = create_refresh_token(identity=student.StudentId)
            session['user_id'] = student.StudentId
            session['user_role'] = 'student'
            
            # session['student_id'] = student.StudentId
            return jsonify({"message": "Login successful"}), 200
        else:
            return jsonify({"message": "Invalid email or password"}), 401
    return jsonify({"message": "Method not allowed"}), 405



@student_api.route('/profile', methods=['GET'])
@role_required('student')
def profile():
    student = getCurrentUser()
    if student:
        return jsonify(student.to_dict())
    else:
        flash('User not found', 'danger')
        return redirect(url_for('student_api.login'))


# Getting the user details
@student_api.route('/', methods=['GET'])
@role_required('student')
def studentData():
    student = getCurrentUser()
    if student:
        json_student_data = getStudentData(student.StudentId)
        if json_student_data:
            return (json_student_data)
        else:
            return jsonify(message="No data available")
    else:
        return render_template('404.html'), 404


# Updating the user details
@student_api.route('/details/update', methods=['POST'])
@role_required('student')
def updateDetails():
    student = getCurrentUser()
    if student:
        if request.method == 'POST':
            email = request.json.get('email')
            number = request.json.get('number')
            residentialAddress = request.json.get('residentialAddress')

            json_result = updateStudentData(
                student.StudentId, email, number, residentialAddress)

            return json_result

        else:
            flash('Invalid email or password', 'danger')
            return redirect(url_for('studentLogin'))
    # else:
    #     return render_template('404.html'), 404


# Changing the password of the user
@student_api.route('/change/password', methods=['POST'])
@role_required('student')
def changePassword():
    student = getCurrentUser()
    if student:
        if request.method == 'POST':
            password = request.json.get('password')
            new_password = request.json.get('new_password')
            confirm_password = request.json.get('confirm_password')

            json_result = updatePassword(
                student.StudentId, password, new_password, confirm_password)

            return json_result

        else:
            flash('Invalid email or password', 'danger')
            return redirect(url_for('studentLogin'))
    else:
        return render_template('404.html'), 404

@student_api.route('/reporting', methods=['POST'])
def reporting():
    
   user = getCurrentUser()
   print('user', user)
   if request.method == 'POST':
        # Handle form submission logic here
        date = request.form['date']
        print('date', date)
        time = request.form['time']
        print('time', time)
        location_id = request.form['location']  # Use the selected location ID
        print('location_id', location_id)
        student_id = request.form['student']
        print('student_id', student_id)
        incident_type_id = request.form['incident']  # Use the selected incident type ID
        print('incident_type_id', incident_type_id)
        description = request.form['description']
        print('description', description)
        try:
            incident = IncidentReport(Date=date, Time=time, LocationId=location_id, StudentId=student_id, IncidentId=incident_type_id, ComplainantId=user.StudentId, Description=description)
            db.session.add(incident)
            db.session.commit()
        except Exception as e:
          print('An exception occurred', e)
        
        flash('Incident reported successfully', 'success')
        return redirect(url_for('studentHome'))
    
# fetch approved reports for student
@student_api.route('/fetch/approved/reports', methods=['GET'])
def approvedReports():
    if request.method == 'GET':
        # Handle form submission logic here
        student_id = session.get('user_id')
        print('student_id', student_id)
        allReports = db.session.query(IncidentReport, Student, Location, IncidentType).join(Student, Student.StudentId == IncidentReport.StudentId).join(Location, Location.LocationId == IncidentReport.LocationId).join(IncidentType, IncidentType.IncidentTypeId == IncidentReport.IncidentId).filter(IncidentReport.StudentId==student_id,IncidentReport.IsAccessible== True, IncidentReport.Status=='approved').order_by(IncidentReport.Date).all()
        list_reports=[]
        print('allReports', allReports)
        if allReports:
            for report in allReports:
                # make a dictionary for reports
                FullName= report.Student.LastName + ", " + report.Student.FirstName
                dict_reports = {
                    'IncidentId': report.IncidentReport.Id,
                    'Date': report.IncidentReport.Date,
                    'Time': report.IncidentReport.Time,
                    'IncidentName': report.IncidentType.Name,
                    'LocationName': report.Location.Name,
                    'StudentName': FullName,
                    'Description': report.IncidentReport.Description,
                    'Status': report.IncidentReport.Status,
                    'Acessibility': report.IncidentReport.IsAccessible

                }
                # append the dictionary to the list
                list_reports.append(dict_reports)
                print('list_reports', list_reports)
            return jsonify({'result': list_reports})
        else :
            return jsonify({'message': 'No reports found'}), 404
        
    
@student_api.route('/reporting_violation', methods=['POST'])
def reporting_violation():
    

   user = getCurrentUser()
   if request.method == 'POST':
        # Handle form submission logic here
        date = request.form['date']
        print('date', date)
        time = request.form['time']
        print('time', time)
        location_id = request.form['location']  # Use the selected location ID
        print('location_id', location_id)
        student_id = request.form['student']
        print('student_id', student_id)
        incident_type_id = request.form['incident']  # Use the selected incident type ID
        print('incident_type_id', incident_type_id)
        description = request.form['description']
        print('description', description)
        
        try:
            violation = ViolationForm(Date=date, Time=time, LocationId=location_id, StudentId=student_id, IncidentId=incident_type_id, ComplainantId=user.StudentId, Description=description)
            db.session.add(violation)
            db.session.commit()
        except Exception as e:
          print('An exception occurred', e)
        
        flash('Incident reported successfully', 'success')
        return redirect(url_for('studentHome'))
            

# fetch approved reports for student
@student_api.route('/fetch/approved/violations', methods=['GET'])
def approvedViolations():
    if request.method == 'GET':
        
        # Handle form submission logic here
        student_id = session.get('user_id')
        allViolations = db.session.query(ViolationForm, Student, Location, IncidentType).join(Student, Student.StudentId == ViolationForm.StudentId).join(Location, Location.LocationId == ViolationForm.LocationId).join(IncidentType, IncidentType.IncidentTypeId == ViolationForm.IncidentId).filter(ViolationForm.StudentId==student_id,ViolationForm.IsAccessible== True).order_by(ViolationForm.Date).all()
        
        list_violations=[]
        if allViolations:
            for violations in allViolations:
                # make a dictionary for reports
                FullName= violations.Student.LastName + ", " + violations.Student.FirstName 
                dict_violation = {
                'ViolationId': violations.ViolationForm.ViolationId,
                'Date': violations.ViolationForm.Date,
                'Time': violations.ViolationForm.Time,
                'IncidentName': violations.IncidentType.Name,
                'LocationName': violations.Location.Name,
                'StudentName': FullName,
                'Complainant': violations.ViolationForm.ComplainantId,
                'Description': violations.ViolationForm.Description,
                'Status': violations.ViolationForm.Status,
                'Acessibility': violations.ViolationForm.IsAccessible

                }
                # append the dictionary to the list
                list_violations.append(dict_violation)
                print('list_violations', list_violations)
            return jsonify({'result': list_violations})
        else :
            return jsonify({'message': 'No reports found'}), 404
            
