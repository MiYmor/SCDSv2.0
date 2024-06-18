# api/api_routes.py
from flask import Blueprint, jsonify, request, redirect, url_for, flash, session, render_template, make_response
from models import Faculty, db, IncidentReport, Student, Location, ViolationForm
import pandas as pd
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from decorators.auth_decorators import role_required
import logging
from .utils import updateFacultyData, getFacultyData, updatePassword, getCurrentUser

import os

from flask_mail import Message
from mail import mail  # Import mail from the mail.py module
from datetime import datetime
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

@faculty_api.route('/sdb', methods=['GET', 'POST'])
def sdbLogin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        teacher = Faculty.query.filter_by(Email=email).first()
        if teacher and check_password_hash(teacher.Password, password):
            # Successfully authenticated
            session['user_id'] = teacher.FacultyId
            session['user_role'] = 'faculty'
            return redirect(url_for('sdbHome'))
        else:
            flash('Invalid email or password', 'danger')
            return redirect(url_for('sdbLogin'))

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

#----------------------------------------------------------------------------------------------------------------

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

@faculty_api.route('/reporting-violation', methods=['POST'])
def reportingViolation():
    user = getCurrentUser()
    if request.method == 'POST':
        try:
            # Handle form submission logic here
            date = request.form['date']
            time = request.form['time']
            location_id = request.form['location']
            student_id = request.form['student']
            incident_type_id = request.form['incident']
            description = request.form['description']
            
            # Get the current date in the desired format (MM/DD/YYYY)
            current_date = datetime.now().strftime('%m/%d/%Y')

            # Create a ViolationForm object with the current date and commit it to the database
            violation = ViolationForm(
                SelfDate=current_date,
                Date=date,
                Time=time,
                LocationId=location_id,
                StudentId=student_id,
                IncidentId=incident_type_id,
                ComplainantId=user.FacultyId,
                Description=description
            )
            
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_data = file.read()  # Read the file data as binary
                violation.AttachmentName = filename
                violation.AttachmentData = file_data  # Store the binary data
            else:
                return jsonify({'message': 'Only PDF files are allowed', 'success': False}), 400
            
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

    # Handle GET request or other methods gracefully
    flash('Invalid request method', 'error')
    return redirect(url_for('facultyHome'))



# Fetch reports CSV from external source and directly send it as attachment

def fetch_report_binary_data(report_id):
    # Assuming you have a model named Report
    report = db.session.query(IncidentReport).filter_by(id=report_id).first()
    if report:
        # Assuming the binary data is stored in a column named 'binary_data'
        return report.binary_data
    else:
        return None

@faculty_api.route('/reporting/<int:report_id>/file', methods=['GET'])
def download_report_file(report_id):
    try:
        # Fetch the binary report data from the database based on report_id
        report = db.session.query(IncidentReport).get(report_id)
        if report and report.AttachmentData:
            # Set the appropriate MIME type for a PDF file
            response = make_response(report.AttachmentData)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = 'attachment; filename=report.pdf'
            return response
        else:
            return {"message": "Failed to fetch report or report not found", "status": 404}
    except Exception as e:
        return {"message": "An error occurred while downloading the file", "status": 500}
    
@faculty_api.route('/assessment/<int:report_id>/file', methods=['GET'])
def download_initial_assessment_file(report_id):
    try:
        # Fetch the binary report data from the database based on report_id
        report = db.session.query(IncidentReport).get(report_id)
        if report and report.InitialAssessmentData:
            # Set the appropriate MIME type for a PDF file
            response = make_response(report.InitialAssessmentData)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = 'attachment; filename=report.pdf'
            return response
        else:
            return {"message": "Failed to fetch report or report not found", "status": 404}
    except Exception as e:
        return {"message": "An error occurred while downloading the file", "status": 500}
    
#================================================================================================================
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
            has_attachment = bool(report.IncidentReport.AttachmentName)
            initial_assessment = bool(report.IncidentReport.FinalAssessmentName)
            final_assessment = bool(report.IncidentReport.FinalAssessmentName)
            dict_reports = {
                'IncidentId': report.IncidentReport.Id,
                'SelfDate': report.IncidentReport.SelfDate,
                'Date': report.IncidentReport.Date,
                'Time': report.IncidentReport.Time,
                'LocationName': report.Location.Name,
                'StudentName': FullName,
                'Investigator': FullNameInvestigator,
                'Complainant': FullNameComplainant,
                'Description': report.IncidentReport.Description,
                'Sanction': report.IncidentReport.Sanction,
                'Status': report.IncidentReport.Status,
                'Acessibility': report.IncidentReport.IsAccessible,
                'AttachmentName': report.IncidentReport.AttachmentName,  # Include the attachment name
                'HasAttachment': has_attachment,  # Include whether the report has an attachment
                'InitialAssessmentName': report.IncidentReport.InitialAssessmentName,
                'InitialAssementData': initial_assessment,
                'FinalAssessmentName': report.IncidentReport.FinalAssessmentName,
                'FinalAssessmentData': final_assessment
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
                'SelfDate': report.IncidentReport.SelfDate,
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

@faculty_api.route('/assign-sanction', methods=['POST'])
def assign_sanction():
    try:
        incident_id = request.form.get('incidentId')
        sanction_description = request.form.get('sanction')
        file = request.files.get('finalAssessment')

        if not incident_id or not sanction_description:
            return jsonify({'error': True, 'message': 'Incident ID and sanction description are required.'}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_data = file.read()

            incident_report = db.session.query(IncidentReport).get(incident_id)
            if incident_report:
                incident_report.Sanction = sanction_description
                incident_report.FinalAssessmentName = filename
                incident_report.FinalAssessmentData = file_data
                db.session.commit()

                return jsonify({'result': True, 'message': 'Sanction assigned successfully'}), 200
            else:
                return jsonify({'error': True, 'message': 'Incident not found'}), 404
        else:
            return jsonify({'error': True, 'message': 'Invalid file type. Only PDF files are allowed.'}), 400

    except Exception as e:
        return jsonify({'error': True, 'message': str(e)}), 500
