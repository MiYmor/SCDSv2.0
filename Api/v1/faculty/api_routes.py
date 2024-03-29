# api/api_routes.py
from flask import Blueprint, jsonify, request, redirect, url_for, flash, session, render_template
from models import Faculty, db, IncidentReport, Student, Location, ViolationForm
import pandas as pd
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash
from decorators.auth_decorators import role_required
import logging
from .utils import updateFacultyData, getFacultyData, updatePassword, getCurrentUser

import os

from flask_mail import Message
from mail import mail  # Import mail from the mail.py module
import secrets
from datetime import datetime, timedelta
faculty_api_base_url = os.getenv("FACULTY_API_BASE_URL")
faculty_api = Blueprint('faculty_api', __name__)

# Api/v1/faculty/api_routes.py
# Define a function to get the current faculty


@faculty_api.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        teacher = Faculty.query.filter_by(Email=email).first()
        if teacher and check_password_hash(teacher.Password, password):
            # Successfully authenticated
            session['user_id'] = teacher.FacultyId
            session['user_role'] = 'faculty'
            return redirect(url_for('facultyHome'))
        else:
            flash('Invalid email or password', 'danger')
            return redirect(url_for('facultyLogin'))


# ===================================================
# TESTING AREA
@faculty_api.route('/profile', methods=['GET'])
@role_required('faculty')
def profile():
    faculty = getCurrentUser()
    if faculty:
        return jsonify(faculty.to_dict())
    else:
        return render_template('404.html'), 404

# ===================================================


# Getting the user (faculty) data
@faculty_api.route('/', methods=['GET'])
@role_required('faculty')
def facultyData():
    faculty = getCurrentUser()
    if faculty:
        json_faculty_data = getFacultyData(faculty.FacultyId)
        if json_faculty_data:
            return (json_faculty_data)
        else:
            return jsonify(message="No user data available")
    else:
        return render_template('404.html'), 404


# UpDate the details of the faculty
@faculty_api.route('/details/update', methods=['GET', 'POST'])
@role_required('faculty')
def upDateDetails():
    faculty = getCurrentUser()
    if faculty:
        if request.method == 'POST':
            email = request.json.get('email')
            number = request.json.get('number')
            residential_address = request.json.get('residential_address')

            json_result = updateFacultyData(
                faculty.FacultyId, email, number, residential_address)

            return json_result

        else:
            flash('Invalid email or password', 'danger')
            return redirect(url_for('facultyLogin'))
    else:
        return render_template('404.html'), 404


# Change the password of the user (faculty)
@faculty_api.route('/change/password', methods=['POST'])
@role_required('faculty')
def changePassword():
    faculty = getCurrentUser()
    if faculty:
        if request.method == 'POST':
            password = request.json.get('password')
            new_password = request.json.get('new_password')
            confirm_password = request.json.get('confirm_password')

            json_result = updatePassword(faculty.FacultyId, password, new_password, confirm_password)

            return json_result

        else:
            flash('Invalid email or password', 'danger')
            return redirect(url_for('facultyLogin'))
    else:
        return render_template('404.html'), 404

#manage cases for faculty
@faculty_api.route('/faculty/manage-reports', methods={'GET', 'POST'})
def manage_reports():
    if request.method == 'POST':
        # Handle the form submission for updating status
        report_id = request.form.get('report_id')
        new_status = request.form.get('new_status')

        try:
            # Assuming you have a model named IncidentReport
            report = db.session.query(IncidentReport).get(report_id)
            if report:
                report.status = new_status
                db.session.commit()
                return redirect(url_for('manage_reports'))
            else:
                return {"message": "Report not found", "status": 404}
        except IntegrityError:
            db.session.rollback()
            return {"message": "Error updating status", "status": 500}

    try:
        # Assuming you have a model named IncidentReport
        reports = db.session.query(IncidentReport).all()

        # Convert the reports data to a DataFrame
        df = pd.DataFrame([{
            'Report ID': report.id,
            'Date': report.Date,
            'Time': report.time,
            'Location': report.location,
            'Student': report.student,
            'Complainant': report.complainant,
            'Description': report.description,
            'Status': report.status,
            # Add other fields as needed
        } for report in reports])

        # Optionally, you can perform additional data manipulations here

        # Save the DataFrame to a CSV file
        df.to_csv('static/csv/reports.csv', index=False)

        return render_template('faculty/manage_report.html', reports=reports)
    except Exception as e:
        return {"message": "An error occurred", "status": 500}

@faculty_api.route('/reporting-violation', methods=['POST'])
def reportingViolation():
   user = getCurrentUser()
   if request.method == 'POST':
        try:
        # Handle form submission logic here
            date = request.form['date']
            time = request.form['time']
            location_id = request.form['location']  # Use the selected location ID
            student_id = request.form['student']
            incident_type_id = request.form['incident']  # Use the selected incident type ID
            description = request.form['description']
            
            violation = ViolationForm(Date=date, Time=time, LocationId=location_id, StudentId=student_id, IncidentId=incident_type_id, ComplainantId=user.FacultyId, Description=description)
            db.session.add(violation)
            db.session.commit()
            
            msg = Message('Violation Reported', sender=("SCDS", "scdspupqc.edu@gmail.com"), recipients=['david.ilustre@gmail.com'])
            msg.body = 'A Violation has been reported. Please check the system for details.'
            mail.send(msg)
            return jsonify({'message': 'Violation reported successfully', 'success': True }), 200
        except Exception as e:
            # Log the exception and display an error message to the user
            print('An exception occurred:', e)
            return jsonify({'message': 'An error occurred while reporting the incident'}), 500

@faculty_api.route('/all-reports', methods={'GET'})
def allReports():    
     #.filter = multiple queries .filter_by = single query
    faculty_id= session.get('user_id')
    allReports = db.session.query(IncidentReport, Student, Location).join(Student, Student.StudentId == IncidentReport.StudentId).join(Location, Location.LocationId == IncidentReport.LocationId).join(Faculty, Faculty.FacultyId == IncidentReport.InvestigatorId).filter(IncidentReport.InvestigatorId == faculty_id, IncidentReport.IsAccessible == True, IncidentReport.Status == 'pending').order_by(IncidentReport.Date).all()
    list_reports=[]
    if allReports:
        for report in allReports:
            # make a dictionary for reports
            investigator = db.session.query(Faculty).filter(Faculty.FacultyId == report.IncidentReport.InvestigatorId).first()
            FullNameInvestigator = investigator.LastName + ", " + investigator.FirstName
            complainant = db.session.query(Student).filter(Student.StudentId == report.IncidentReport.ComplainantId).first()
            FullNameComplainant = complainant.LastName + ", " + complainant.FirstName
            FullName= report.Student.LastName + ", " + report.Student.FirstName 
            dict_reports = {
                'IncidentId': report.IncidentReport.Id,
                'Date': report.IncidentReport.Date,
                'Time': report.IncidentReport.Time,
                'LocationName': report.Location.Name,
                'StudentName': FullName,
                'Investigator': FullNameInvestigator,
                'Complainant': FullNameComplainant,
                'Description': report.IncidentReport.Description,
                'Sanction': report.IncidentReport.Sanction,
                'Status': report.IncidentReport.Status,
                'Acessibility': report.IncidentReport.IsAccessible
            }
            # append the dictionary to the list
            list_reports.append(dict_reports)
        return jsonify({'result': list_reports})

@faculty_api.route('/all-approve-reports', methods={'GET'})
def allapprovedReports():    
     #.filter = multiple queries .filter_by = single query
    faculty_id= session.get('user_id')
    allReports = db.session.query(IncidentReport, Student, Location).join(Student, Student.StudentId == IncidentReport.StudentId).join(Location, Location.LocationId == IncidentReport.LocationId).join(Faculty, Faculty.FacultyId == IncidentReport.InvestigatorId).filter(IncidentReport.InvestigatorId == faculty_id, IncidentReport.IsAccessible == True, IncidentReport.Status == 'approved').order_by(IncidentReport.Date).all()
    list_reports=[]
    if allReports:
        for report in allReports:
            # make a dictionary for reports
            investigator = db.session.query(Faculty).filter(Faculty.FacultyId == report.IncidentReport.InvestigatorId).first()
            FullNameInvestigator = investigator.LastName + ", " + investigator.FirstName
            complainant = db.session.query(Student).filter(Student.StudentId == report.IncidentReport.ComplainantId).first()
            FullNameComplainant = complainant.LastName + ", " + complainant.FirstName
            FullName= report.Student.LastName + ", " + report.Student.FirstName 
            dict_reports = {
                'IncidentId': report.IncidentReport.Id,
                'Date': report.IncidentReport.Date,
                'Time': report.IncidentReport.Time,
                'LocationName': report.Location.Name,
                'StudentName': FullName,
                'Investigator': FullNameInvestigator,
                'Complainant': FullNameComplainant,
                'Description': report.IncidentReport.Description,
                'Sanction': report.IncidentReport.Sanction,
                'Status': report.IncidentReport.Status,
                'Acessibility': report.IncidentReport.IsAccessible
            }
            # append the dictionary to the list
            list_reports.append(dict_reports)
        return jsonify({'result': list_reports})


@faculty_api.route('/assign-sanction', methods={'POST'})
def assignSanction():
    try:
        # Assuming the incoming data is JSON
        data = request.get_json()
        # Extract incidentId and assignedFaculty from the JSON payload
        incident_id = data.get('incidentId')
        print('Received incidentId:', incident_id)
        
        manage_sanction = data.get('assignSanction')
        print('Received Sabction:', manage_sanction)

        # Query the incident report
        report = IncidentReport.query.filter_by(Id=incident_id).first()

        # Check if the incident report is found
        if report:
            # Update InvestigatorId with assigned_faculty
            report.Sanction = manage_sanction
            # Commit the changes to the database
            db.session.commit()
            # Return a success message
            return jsonify({'result': 'success', 'message': 'Report approved'})
        else:
            # Return an error message if the incident report is not found
            return jsonify({'error': 'failed', 'message': 'Report not found'})
    except Exception as e:
        print('error',e) 
        # Return an error message if an exception occurs
        return jsonify({'error': 'failed', 'message': str(e)})
    