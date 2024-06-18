# api/api_routes.py
from flask import Blueprint, jsonify, request, redirect, url_for, flash, session, render_template, make_response
from flask_mail import Message, Mail
from mail import mail
from models import SystemAdmin, db, IncidentReport, Student, Location, IncidentType, Faculty, ViolationForm, FacultyIncidentReport
import pandas as pd

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash
from decorators.auth_decorators import role_required

from .utils import getCurrentUser

import base64
import os

system_admin_api = Blueprint('system_admin_api',__name__)
system_admin_api_base_url = os.getenv("SYSTEM_ADMIN_API_BASE_URL")

@system_admin_api.route('/login2', methods=['POST'])
def login2():
    print("CHECKING SYSTEM LOGIN")
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        print("CHECKING SYSTEM LOGIN")
        systemAdmin = SystemAdmin.query.filter_by(Email=email).first()
        if systemAdmin and check_password_hash(systemAdmin.Password, password):
            session['user_id'] = systemAdmin.SysAdminId
            session['user_role'] = 'systemAdmin'
            print("SUCCESSFUL LOGIN")
            return redirect(url_for('systemAdminHome'))
        else:
            flash('Invalid email or password', 'danger')
            print("FAILED LOGIN")
            return redirect(url_for('systemAdminLogin'))
    return redirect(url_for('systemAdminLogin'))


@system_admin_api.route('/ads', methods=['GET'])
def helo():
    print("CHECKING SYSTEM LOGIN")
    return ({"message": " HELLO THERE FROM RTHIS"})

# to display all the reports
@system_admin_api.route('/systemadmin/manage-reports', methods={'GET', 'POST'})
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
            'Date': report.date,
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

        return render_template('systemadmin/manage_report.html', reports=reports)
    except Exception as e:
        return {"message": "An error occurred", "status": 500}

# to display all the reports
@system_admin_api.route('/systemadmin/manage-faculty-case', methods={'GET', 'POST'})
def manage_faculty_case():
    if request.method == 'POST':
        # Handle the form submission for updating status
        report_id = request.form.get('report_id')
        new_status = request.form.get('new_status')

        try:
            # Assuming you have a model named IncidentReport
            report = db.session.query(FacultyIncidentReport).get(report_id)
            if report:
                report.status = new_status
                db.session.commit()
                return redirect(url_for('manage_faculty_case'))
            else:
                return {"message": "Report not found", "status": 404}
        except IntegrityError:
            db.session.rollback()
            return {"message": "Error updating status", "status": 500}

    try:
        # Assuming you have a model named IncidentReport
        reports = db.session.query(FacultyIncidentReport).all()

        # Convert the reports data to a DataFrame
        df = pd.DataFrame([{
            'Report ID': report.id,
            'Date': report.date,
            'Time': report.time,
            'Location': report.location,
            'Faculty': report.faculty,
            'Complainant': report.complainant,
            'Description': report.description,
            'Status': report.status,
            # Add other fields as needed
        } for report in reports])

        # Optionally, you can perform additional data manipulations here

        # Save the DataFrame to a CSV file
        df.to_csv('static/csv/reports.csv', index=False)

        return render_template('systemadmin/manage_faculty_case.html', reports=reports)
    except Exception as e:
        return {"message": "An error occurred", "status": 500}
    
#to fetch all violation available
@system_admin_api.route('/systemadmin/manage-violation', methods={'GET', 'POST'})
def manage_violations():
    if request.method == 'POST':
        # Handle the form submission for updating status
        violation_id = request.form.get('violation_id')
        new_status = request.form.get('new_status')

        try:
            # Assuming you have a model named IncidentReport
            violation = db.session.query(ViolationForm).get(violation_id)
            if violation:
                violation.status = new_status
                db.session.commit()
                return redirect(url_for('manage_violations'))
            else:
                return {"message": "Report not found", "status": 404}
        except IntegrityError:
            db.session.rollback()
            return {"message": "Error updating status", "status": 500}

    try:
        # Assuming you have a model named IncidentReport
        violations = db.session.query(ViolationForm).all()

        # Convert the reports data to a DataFrame
        df = pd.DataFrame([{
            'Violation ID': violation.ViolationId,
            'Date': violation.date,
            'Time': violation.time,
            'Incident Type': violation.incident_type,
            'Location': violation.location,
            'Student': violation.student,
            'Complainant': violation.complainant,
            'Description': violation.description,
            'Status': violation.status,
            # Add other fields as needed
        } for violation in violations])

        # Optionally, you can perform additional data manipulations here

        # Save the DataFrame to a CSV file
        df.to_csv('static/csv/violations.csv', index=False)

        return render_template('systemadmin/manage_violation.html', violations=violations)
    except Exception as e:
        return {"message": "An error occurred", "status": 500}


# Fetch reports CSV from external source and directly send it as attachment

def fetch_report_binary_data(report_id):
    # Assuming you have a model named Report
    report = db.session.query(IncidentReport).filter_by(id=report_id).first()
    if report:
        # Assuming the binary data is stored in a column named 'binary_data'
        return report.binary_data
    else:
        return None



@system_admin_api.route('/reporting/<int:report_id>/file', methods=['GET'])
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

# Fetch reports CSV from external source and directly send it as attachment

def fetch_faculty_report_binary_data(report_id):
    # Assuming you have a model named Report
    report = db.session.query(FacultyIncidentReport).filter_by(id=report_id).first()
    if report:
        # Assuming the binary data is stored in a column named 'binary_data'
        return report.binary_data
    else:
        return None

@system_admin_api.route('/faculty/reporting/<int:report_id>/file', methods=['GET'])
def download_faculty_report_file(report_id):
    try:
        # Fetch the binary report data from the database based on report_id
        report = db.session.query(FacultyIncidentReport).get(report_id)
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

def fetch_violation_binary_data(violation_id):
    # Assuming you have a model named Report
    violations = db.session.query(ViolationForm).filter_by(id=violation_id).first()
    if violations:
        # Assuming the binary data is stored in a column named 'binary_data'
        return violations.binary_data
    else:
        return None

@system_admin_api.route('/violation/<int:violation_id>/file', methods=['GET'])
def download_violation_file(violation_id):
    try:
        # Fetch the binary report data from the database based on report_id
        violations = db.session.query(ViolationForm).get(violation_id)
        if violations and violations.AttachmentData:
            # Set the appropriate MIME type for a PDF file
            response = make_response(violations.AttachmentData)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = 'attachment; filename=report.pdf'
            return response
        else:
            return {"message": "Failed to fetch report or report not found", "status": 404}
    except Exception as e:
        return {"message": "An error occurred while downloading the file", "status": 500}

#================================================================================================
#Assessment File Donwload
@system_admin_api.route('/assessment/<int:report_id>/file', methods=['GET'])
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
    
@system_admin_api.route('/final/assessment/<int:report_id>/file', methods=['GET'])
def download_final_assessment_file(report_id):
    try:
        # Fetch the binary report data from the database based on report_id
        report = db.session.query(IncidentReport).get(report_id)
        if report and report.FinalAssessmentData:
            # Set the appropriate MIME type for a PDF file
            response = make_response(report.FinalAssessmentData)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = 'attachment; filename=report.pdf'
            return response
        else:
            return {"message": "Failed to fetch report or report not found", "status": 404}
    except Exception as e:
        return {"message": "An error occurred while downloading the file", "status": 500}
    
#================================================================================================
@system_admin_api.route('/all-reports', methods={'GET'})
def allReports():
    allReports = db.session.query(IncidentReport, Student, Location).join(Student, Student.StudentId == IncidentReport.StudentId).join(Location, Location.LocationId == IncidentReport.LocationId).filter(IncidentReport.IsAccessible == False, IncidentReport.Status == 'pending').order_by(IncidentReport.Date).all()
    list_reports=[]
    if allReports:
        for report in allReports:
            complainant = db.session.query(Student).filter(Student.StudentId == report.IncidentReport.ComplainantId).first()
            FullNameComplainant = complainant.LastName + ", " + complainant.FirstName
            FullName= report.Student.LastName + ", " + report.Student.FirstName
            # Check if the report has an attachment
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
                'Complainant': FullNameComplainant,
                'Description': report.IncidentReport.Description,
                'Status': report.IncidentReport.Status,
                'Acessibility': report.IncidentReport.IsAccessible,
                'AttachmentName': report.IncidentReport.AttachmentName,  # Include the attachment name
                'HasAttachment': has_attachment,  # Include whether the report has an attachment
                'InitialAssessmentName': report.IncidentReport.InitialAssessmentName,
                'InitialAssementData': initial_assessment,
                'FinalAssessmentName': report.IncidentReport.FinalAssessmentName,
                'FinalAssessmentData': final_assessment
            }
            list_reports.append(dict_reports)
        return jsonify({'result': list_reports})


# fetch all the faculty case that are available
@system_admin_api.route('/all-faculty-case', methods={'GET'})
def allFacultyCase():
    #.filter = multiple queries .filter_by = single query
    allFacultyCase = db.session.query(FacultyIncidentReport, Faculty, Location).join(Faculty, Faculty.FacultyId == FacultyIncidentReport.FacultyId).join(Location, Location.LocationId == FacultyIncidentReport.LocationId).filter(FacultyIncidentReport.IsAccessible == False, FacultyIncidentReport.Status == 'pending').order_by(FacultyIncidentReport.Date).all()
    list_reports=[]
    if allFacultyCase:
        for report in allFacultyCase:
            # make a dictionary for reports
            complainant = db.session.query(Student).filter(Student.StudentId == report.FacultyIncidentReport.ComplainantId).first()
            FullNameComplainant = complainant.LastName + ", " + complainant.FirstName
            FullName= report.Faculty.LastName + ", " + report.Faculty.FirstName
            # Check if the report has an attachment
            has_attachment = bool(report.FacultyIncidentReport.AttachmentName)
            dict_reports = {
                'CaseId': report.FacultyIncidentReport.Id,
                'SelfDate': report.FacultyIncidentReport.SelfDate,
                'Date': report.FacultyIncidentReport.Date,
                'Time': report.FacultyIncidentReport.Time,
                'LocationName': report.Location.Name,
                'FacultyName': FullName,
                'Complainant': FullNameComplainant,
                'Description': report.FacultyIncidentReport.Description,
                'Status': report.FacultyIncidentReport.Status,
                'Acessibility': report.FacultyIncidentReport.IsAccessible,
                'AttachmentName': report.FacultyIncidentReport.AttachmentName,  # Include the attachment name
                'HasAttachment': has_attachment  # Include whether the report has an attachment

            }
            # append the dictionary to the list
            list_reports.append(dict_reports)
        return jsonify({'result': list_reports})
    
# fetch all the violations that are available
@system_admin_api.route('/all-violations', methods={'GET'})
def allViolations():
    #.filter = multiple queries .filter_by = single query
    allViolations = db.session.query(ViolationForm, Student, Location, IncidentType).join(Student, Student.StudentId == ViolationForm.StudentId).join(Location, Location.LocationId == ViolationForm.LocationId).join(IncidentType, IncidentType.IncidentTypeId == ViolationForm.IncidentId).filter(ViolationForm.IsAccessible == False, ViolationForm.Status != 'removed').order_by(ViolationForm.Date).all()
    list_violations=[]
    if allViolations:
        for violations in allViolations:
            # make a dictionary for reports
            complainant = db.session.query(Faculty).filter(Faculty.FacultyId == violations.ViolationForm.ComplainantId).first()
            FullNameComplainant = complainant.LastName + ", " + complainant.FirstName
            FullName= violations.Student.LastName + ", " + violations.Student.FirstName 
            has_attachment = bool(violations.ViolationForm.AttachmentName)
            dict_violation = {
                'ViolationId': violations.ViolationForm.ViolationId,
                'SelfDate': violations.ViolationForm.SelfDate,
                'Date': violations.ViolationForm.Date,
                'Time': violations.ViolationForm.Time,
                'IncidentName': violations.IncidentType.Name,
                'LocationName': violations.Location.Name,
                'StudentName': FullName,
                'Complainant': FullNameComplainant,
                'Description': violations.ViolationForm.Description,
                'Status': violations.ViolationForm.Status,
                'Acessibility': violations.ViolationForm.IsAccessible,
                'AttachmentName': violations.ViolationForm.AttachmentName, # Include the attachment name
                'HasAttachment': has_attachment  # Include whether the report has an attachment

            }
            # append the dictionary to the list
            list_violations.append(dict_violation)
        return jsonify({'result': list_violations})
    
    
#================================================================================================
# get all the case that are closed
@system_admin_api.route('/closed-case', methods=['GET'])
def allClosedCase():
    allClosedCase = db.session.query(IncidentReport, Student, Location, Faculty).join(Student, Student.StudentId == IncidentReport.StudentId).join(Location, Location.LocationId == IncidentReport.LocationId).join(Faculty, Faculty.FacultyId == IncidentReport.InvestigatorId).filter(IncidentReport.IsAccessible == True, IncidentReport.Status =='pending').order_by(IncidentReport.Date).all()
    
    unique_reports = set()  # Set to store unique report IDs
    list_closedcase=[]

    if allClosedCase:
        for report in allClosedCase:
            report_id = report.IncidentReport.Id
            if report_id not in unique_reports:  # Check if the report ID is unique
                unique_reports.add(report_id)  # Add report ID to set
                investigator = db.session.query(Faculty).filter(Faculty.FacultyId == report.IncidentReport.InvestigatorId).first()
                FullNameInvestigator = investigator.LastName + ", " + investigator.FirstName
                complainant = db.session.query(Student).filter(Student.StudentId == report.IncidentReport.ComplainantId).first()
                FullNameComplainant = complainant.LastName + ", " + complainant.FirstName
                FullName= report.Student.LastName + ", " + report.Student.FirstName
                has_attachment = bool(report.IncidentReport.AttachmentName)
                initial_assessment = bool(report.IncidentReport.FinalAssessmentName)
                final_assessment = bool(report.IncidentReport.FinalAssessmentName) 
                dict_closedcase = {
                    'IncidentId': report_id,
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
                list_closedcase.append(dict_closedcase)
        return jsonify({'result': list_closedcase})  # Move this line outside the loop
    else:
        return jsonify({'result': []})  # Return an empty list if no closed cases are found


        
# get all the case that are closed
@system_admin_api.route('/resolved-case', methods=['GET'])
def allResolvedCase():
    allResolvedCase = db.session.query(IncidentReport, Student, Location) \
        .join(Student, Student.StudentId == IncidentReport.StudentId) \
        .join(Location, Location.LocationId == IncidentReport.LocationId) \
        .filter(IncidentReport.IsAccessible == True, IncidentReport.Status != 'pending') \
        .order_by(IncidentReport.Date).all()
    
    list_resolvedcase = []

    if allResolvedCase:
        for report in allResolvedCase:
            # Fetch investigator
            investigator = db.session.query(Faculty).filter(Faculty.FacultyId == report.IncidentReport.InvestigatorId).first()
            if investigator:
                FullNameInvestigator = investigator.LastName + ", " + investigator.FirstName
            else:
                FullNameInvestigator = "None"

            # Fetch complainant
            complainant = db.session.query(Student).filter(Student.StudentId == report.IncidentReport.ComplainantId).first()
            if complainant:
                FullNameComplainant = complainant.LastName + ", " + complainant.FirstName
            else:
                FullNameComplainant = "Complainant not found"

            # Student's full name
            FullName = report.Student.LastName + ", " + report.Student.FirstName
            has_attachment = bool(report.IncidentReport.AttachmentName)
            initial_assessment = bool(report.IncidentReport.FinalAssessmentName)
            final_assessment = bool(report.IncidentReport.FinalAssessmentName)
            # Create a dictionary for the report
            dict_resolvedcase = {
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

            # Append the dictionary to the list
            list_resolvedcase.append(dict_resolvedcase)

    return jsonify({'result': list_resolvedcase})
        
#================================================================================================
@system_admin_api.route('/all-resolved-faculty-case', methods={'GET'})
def allResolvedFacultyCase():
    #.filter = multiple queries .filter_by = single query
    allResolvedFacultyCase = db.session.query(FacultyIncidentReport, Faculty, Location).join(Faculty, Faculty.FacultyId == FacultyIncidentReport.FacultyId).join(Location, Location.LocationId == FacultyIncidentReport.LocationId).filter(FacultyIncidentReport.IsAccessible == False, FacultyIncidentReport.Status == 'approved').order_by(FacultyIncidentReport.Date).all()
    list_reports=[]
    if allResolvedFacultyCase:
        for report in allResolvedFacultyCase:
            # make a dictionary for reports
            complainant = db.session.query(Student).filter(Student.StudentId == report.FacultyIncidentReport.ComplainantId).first()
            FullNameComplainant = complainant.LastName + ", " + complainant.FirstName
            FullName= report.Faculty.LastName + ", " + report.Faculty.FirstName
            has_attachment = bool(report.FacultyIncidentReport.AttachmentName)
            dict_reports = {
                'CaseId': report.FacultyIncidentReport.Id,
                'SelfDate': report.FacultyIncidentReport.SelfDate,
                'Date': report.FacultyIncidentReport.Date,
                'Time': report.FacultyIncidentReport.Time,
                'LocationName': report.Location.Name,
                'FacultyName': FullName,
                'Complainant': FullNameComplainant,
                'Description': report.FacultyIncidentReport.Description,
                'Status': report.FacultyIncidentReport.Status,
                'Acessibility': report.FacultyIncidentReport.IsAccessible,
                'AttachmentName': report.FacultyIncidentReport.AttachmentName,  # Include the attachment name
                'HasAttachment': has_attachment  # Include whether the report has an attachment
            }
            # append the dictionary to the list
            list_reports.append(dict_reports)
        return jsonify({'result': list_reports})

@system_admin_api.route('/all-removed=faculty-case', methods={'GET'})
def allRemovedFacultyCase():
    #.filter = multiple queries .filter_by = single query
    allRemovedFacultyCase = db.session.query(FacultyIncidentReport, Faculty, Location).join(Faculty, Faculty.FacultyId == FacultyIncidentReport.FacultyId).join(Location, Location.LocationId == FacultyIncidentReport.LocationId).filter(FacultyIncidentReport.IsAccessible == False, FacultyIncidentReport.Status == 'removed').order_by(FacultyIncidentReport.Date).all()
    list_reports=[]
    if allRemovedFacultyCase:
        for report in allRemovedFacultyCase:
            # make a dictionary for reports
            complainant = db.session.query(Student).filter(Student.StudentId == report.FacultyIncidentReport.ComplainantId).first()
            FullNameComplainant = complainant.LastName + ", " + complainant.FirstName
            FullName= report.Faculty.LastName + ", " + report.Faculty.FirstName
            dict_reports = {
                'CaseId': report.FacultyIncidentReport.Id,
                'SelfDate': report.FacultyIncidentReport.SelfDate,
                'Date': report.FacultyIncidentReport.Date,
                'Time': report.FacultyIncidentReport.Time,
                'LocationName': report.Location.Name,
                'FacultyName': FullName,
                'Complainant': FullNameComplainant,
                'Description': report.FacultyIncidentReport.Description,
                'Status': report.FacultyIncidentReport.Status,
                'Acessibility': report.FacultyIncidentReport.IsAccessible

            }
            # append the dictionary to the list
            list_reports.append(dict_reports)
        return jsonify({'result': list_reports})
#================================================================================================
@system_admin_api.route('/all-closed-violations', methods={'GET'})
def allClosedViolations():
    #.filter = multiple queries .filter_by = single query
    allClosedViolations = db.session.query(ViolationForm, Student, Location, IncidentType).join(Student, Student.StudentId == ViolationForm.StudentId).join(Location, Location.LocationId == ViolationForm.LocationId).join(IncidentType, IncidentType.IncidentTypeId == ViolationForm.IncidentId).filter(ViolationForm.IsAccessible == True, ViolationForm.Status != 'pending').order_by(ViolationForm.Date).all()
    list_closedviolations=[]
    if allClosedViolations:
        for violations in allClosedViolations:
            # make a dictionary for reports
            complainant = db.session.query(Faculty).filter(Faculty.FacultyId == violations.ViolationForm.ComplainantId).first()
            FullNameComplainant = complainant.LastName + ", " + complainant.FirstName
            FullName= violations.Student.LastName + ", " + violations.Student.FirstName 
            has_attachment = bool(violations.ViolationForm.AttachmentName)
            dict_closedviolation = {
                'ViolationId': violations.ViolationForm.ViolationId,
                'SelfDate': violations.ViolationForm.SelfDate,
                'Date': violations.ViolationForm.Date,
                'Time': violations.ViolationForm.Time,
                'IncidentName': violations.IncidentType.Name,
                'LocationName': violations.Location.Name,
                'StudentName': FullName,
                'Complainant': FullNameComplainant,
                'Description': violations.ViolationForm.Description,
                'Status': violations.ViolationForm.Status,
                'Acessibility': violations.ViolationForm.IsAccessible,
                'AttachmentName': violations.ViolationForm.AttachmentName, # Include the attachment name
                'HasAttachment': has_attachment  # Include whether the report has an attachment
            }
            # append the dictionary to the list
            list_closedviolations.append(dict_closedviolation)
        return jsonify({'result': list_closedviolations})

@system_admin_api.route('/all-removed-violations', methods={'GET'})
def allRemovedViolations():
    #.filter = multiple queries .filter_by = single query
    allRemovedViolations = db.session.query(ViolationForm, Student, Location, IncidentType).join(Student, Student.StudentId == ViolationForm.StudentId).join(Location, Location.LocationId == ViolationForm.LocationId).join(IncidentType, IncidentType.IncidentTypeId == ViolationForm.IncidentId).filter(ViolationForm.Status == 'removed').order_by(ViolationForm.Date).all()
    list_removedviolations=[]
    if allRemovedViolations:
        for violations in allRemovedViolations:
            # make a dictionary for reports
            #get the student id usinng the violationform.complainantid
            complainant = db.session.query(Faculty).filter(Faculty.FacultyId == violations.ViolationForm.ComplainantId).first()
            FullNameComplainant = complainant.LastName + ", " + complainant.FirstName
            FullName= violations.Student.LastName + ", " + violations.Student.FirstName 
            dict_removedviolation = {
                'ViolationId': violations.ViolationForm.ViolationId,
                'SelfDate': violations.ViolationForm.SelfDate,
                'Date': violations.ViolationForm.Date,
                'Time': violations.ViolationForm.Time,
                'IncidentName': violations.IncidentType.Name,
                'LocationName': violations.Location.Name,
                'StudentName': FullName,
                'Complainant': FullNameComplainant,
                'Description': violations.ViolationForm.Description,
                'Status': violations.ViolationForm.Status,
                'Acessibility': violations.ViolationForm.IsAccessible
            }
            # append the dictionary to the list
            list_removedviolations.append(dict_removedviolation)
        return jsonify({'result': list_removedviolations})



#================================================================================================
# to approve the case or open the case 
@system_admin_api.route('/access-report', methods={'POST'})
def accessReports():    
     # Assuming the incoming data is JSON
    data = request.get_json()
    # Extract incidentId from the JSON payload
    incident_id = data.get('IncidentId')
    name = data.get('Name')
    # Your logic to handle the incidentId
    print('Received incidentId:', incident_id)
    # make a querry calling the incidentreport table
    incident = IncidentReport.query.filter_by(Id=incident_id).first()
    # if the incident is found
    if incident:
        # change the status to approved
        incident.IsAccessible = True
        # commit the changes
        db.session.commit()
        try:
            # Compose the email message
            msg = Message('Notification of Case Assignment: Investigation of Student Matter', sender=("SCDS", "scdspupqc.edu@gmail.com"), recipients=['david.ilustre@gmail.com'])
            msg.html = render_template('email_templates/faculty_notyf_case.html', caseId=incident_id)
                # Send the email
            mail.send(msg)
            # Return a success response
            return jsonify({'result': 'success', 'message': 'Case approved and email notification sent'})
        except Exception as e:
            # Log the exception and return an error response
            print('An error occurred while sending the email notification:', e)
            return jsonify({'error': 'failed', 'message': 'Case approved, but email notification failed'}), 500
    else:
        # Return a message
        return jsonify({'error': 'failed', 'message': 'Report not found'})

# to close the case 
@system_admin_api.route('/remove-access-report', methods=['POST'])
def removeAccessReports():
    # Assuming the incoming data is JSON
    data = request.get_json()
    # Extract incidentId from the JSON payload
    incident_id = data.get('IncidentId')
    
    # Query the IncidentReport table for the incident with given ID
    incident = IncidentReport.query.filter_by(Id=incident_id).first()

    # If the incident is found
    if incident:
        # Update the incident attributes
        incident.IsAccessible = False
        incident.Sanction = 'pending'
        incident.Status = 'pending'
        incident.InvestigatorId = None
        incident.InitialAssessmentName = None
        incident.InitialAssessmentData = None
        incident.FinalAssessmentName = None
        incident.FinalAssessmentData = None

        # Commit the changes to the database
        db.session.commit()
        
        # Return success message
        return jsonify({'result': 'success', 'message': 'Access report removed successfully'})
    else:
        # Return error message if incident is not found
        return jsonify({'error': 'failed', 'message': 'Incident not found'})

    

@system_admin_api.route('/resolved-precase', methods=['POST'])
def resolvePrecase():
    try:
        # Check if the form data includes a file
        if 'file' not in request.files:
            return jsonify({'error': 'failed', 'message': 'No file part'})
        file = request.files['file']
        # Validate that the file is a PDF
        if file.filename == '':
            return jsonify({'error': 'failed', 'message': 'No selected file'})
        
        if file and not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'failed', 'message': 'Invalid file type. Only PDFs are allowed'})
        # Read file data
        file_data = file.read()
        # Assuming the other incoming data is in form data format
        incident_id = request.form.get('incidentId')
        # Query the incident report
        report = IncidentReport.query.filter_by(Id=incident_id).first()
        # Check if the incident report is found
        if report:
            # Update FinalAssessmentName and FinalAssessmentData
            report.IsAccessible = True
            report.Sanction = 'None'
            report.Status = 'resolved'
            report.FinalAssessmentName = file.filename
            report.FinalAssessmentData = file_data
            
            db.session.commit()
            return jsonify({'result': 'success', 'message': 'Final assessment uploaded successfully'})
        else:
            return jsonify({'error': 'failed', 'message': 'Incident report not found'})
    except Exception as e:
        # Handle the exception here
        print(e)
        return jsonify({'error': 'failed', 'message': 'An error occurred'})


@system_admin_api.route('/resolve-faculty-case', methods={'POST'})
def resolveFacultyCase():    
     # Assuming the incoming data is JSON
    data = request.get_json()
    # Extract incidentId from the JSON payload
    case_id = data.get('CaseId')
    # Your logic to handle the incidentId
    print('Received CaseId:', case_id)
    # make a querry calling the incidentreport table
    incident = FacultyIncidentReport.query.filter_by(Id=case_id).first()
    # if the incident is found
    if incident:
        # change the status to approved
        incident.Status = 'approved'
        # commit the changes
        db.session.commit()
        # return a message
        return jsonify({'result': 'success', 'message': 'Report approved'})
    else:
        # return a message
        return jsonify({'error': 'failed', 'message': 'Report not found'})

@system_admin_api.route('/reopen-faculty-case', methods={'POST'})
def reopenFacultyCase():    
     # Assuming the incoming data is JSON
    data = request.get_json()
    # Extract incidentId from the JSON payload
    case_id = data.get('CaseId')
    # Your logic to handle the incidentId
    print('Received CaseId:', case_id)
    # make a querry calling the incidentreport table
    incident = FacultyIncidentReport.query.filter_by(Id=case_id).first()
    # if the incident is found
    if incident:
        # change the status to approved
        incident.Status = 'pending'
        # commit the changes
        db.session.commit()
        # return a message
        return jsonify({'result': 'success', 'message': 'Report approved'})
    else:
        # return a message
        return jsonify({'error': 'failed', 'message': 'Report not found'})
    
    
#================================================================================================
@system_admin_api.route('/reopen-report', methods={'POST'})
def reopenReports():    
     # Assuming the incoming data is JSON
    data = request.get_json()
    # Extract incidentId from the JSON payload
    incident_id = data.get('IncidentId')
    # Your logic to handle the incidentId
    print('Received incidentId:', incident_id)
    # make a querry calling the incidentreport table
    incident = IncidentReport.query.filter_by(Id=incident_id).first()
    # if the incident is found
    if incident:
        # change the status to approved
        incident.IsAccessible = False
        incident.Sanction = 'pending'
        incident.Status = 'pending'
        incident.InvestigatorId = None
        incident.InitialAssessmentName = None
        incident.InitialAssessmentData = None
        incident.FinalAssessmentName = None
        incident.FinalAssessmentData = None
        # commit the changes
        db.session.commit()
        # return a message
        return jsonify({'result': 'success', 'message': 'Report approved'})
    else:
        # return a message
        return jsonify({'error': 'failed', 'message': 'Report not found'})


@system_admin_api.route('/approve-report', methods={'POST'})
def approveReport():    
    # Assuming the incoming data is JSON
    data = request.get_json()
    # Extract incidentId from the JSON payload
    incident_id = data.get('IncidentId')
    name = data.get('Name')
    sanction = data.get('Sanction')
    # Your logic to handle the incidentId
    print('Received incidentId:', incident_id)
    # make a query calling the incidentreport table
    incident = IncidentReport.query.filter_by(Id=incident_id).first()
    # if the incident is found
    if incident:
        # change the status to approved
        incident.Status = 'approved'
        # commit the changes
        db.session.commit()
        try:
                # Compose the email message with HTML content
            msg = Message('Notification of Case Involvement', sender=("SCDS", "scdspupqc.edu@gmail.com"), recipients=['david.ilustre@gmail.com'])
                
            msg.html = render_template('email_templates/student_notyf_case.html', caseId=incident_id,name=name, sanction=sanction)
                # Send the email
            mail.send(msg)
                # Return a success response
            return jsonify({'result': 'success', 'message': 'Report approved and email notification sent'})
        except Exception as e:
            # Log the exception and return an error response
            print('An error occurred while sending the email notification:', e)
            return jsonify({'error': 'failed', 'message': 'Report approved, but email notification failed'}), 500
    else:
        # Return a message
        return jsonify({'error': 'failed', 'message': 'Report not found'})


# to approve the case or open the case 
@system_admin_api.route('/access-violation', methods={'POST'})
def accessViolations():    
     # Assuming the incoming data is JSON
    data = request.get_json()
    # Extract incidentId from the JSON payload
    violation_id = data.get('ViolationId')
    name = data.get('Name')
    sanction = data.get('Sanction')
    # Your logic to handle the incidentId
    print('Received ViolationId:', violation_id)
    # make a querry calling the incidentreport table
    violation = ViolationForm.query.filter_by(ViolationId=violation_id).first()
    # if the incident is found
    if violation:
        # change the status to approved
        violation.IsAccessible = True
        # commit the changes
        db.session.commit()
        try:
            # Compose the email message
            msg = Message('Notification of Violation Involvement', sender=("SCDS", "scdspupqc.edu@gmail.com"), recipients=['david.ilustre@gmail.com'])
            msg.html = render_template('email_templates/violation_notyf.html', violationId=violation_id, name=name, sanction=sanction)
            # Send the email
            mail.send(msg)
            # Return a success response
            return jsonify({'result': 'success', 'message': 'Violation approved and email notification sent'})
        except Exception as e:
            # Log the exception and return an error response
            print('An error occurred while sending the email notification:', e)
            return jsonify({'error': 'failed', 'message': 'Violation approved, but email notification failed'}), 500
    else:
        # Return a message
        return jsonify({'error': 'failed', 'message': 'Violation not found'})

# to close the case 
@system_admin_api.route('/remove-access-violation', methods={'POST'})
def removeAccessViolations():
     # Assuming the incoming data is JSON
    data = request.get_json()
    # Extract incidentId from the JSON payload
    violation_id = data.get('ViolationId')
    # Your logic to handle the incidentId
    print('Received ViolationId:', violation_id)
    # make a querry calling the incidentreport table
    violation = ViolationForm.query.filter_by(ViolationId=violation_id).first()
    # if the incident is found
    if violation:
        # change the status to approved
        violation.IsAccessible = False
        # commit the changes
        db.session.commit()
        # return a message
        return jsonify({'result': 'success', 'message': 'Report approved'})
    else:
        # return a message
        return jsonify({'error': 'failed', 'message': 'Report not found'})
    
# to remove the violation
@system_admin_api.route('/remove-violation', methods={'POST'})
def removeViolations():
     # Assuming the incoming data is JSON
    data = request.get_json()
    # Extract incidentId from the JSON payload
    violation_id = data.get('ViolationId')
    # Your logic to handle the incidentId
    print('Received ViolationId:', violation_id)
    # make a querry calling the incidentreport table
    violation = ViolationForm.query.filter_by(ViolationId=violation_id).first()
    # if the incident is found
    if violation:
        # change the status to approved
        violation.Status = 'removed'
        # commit the changes
        db.session.commit()
        # return a message
        return jsonify({'result': 'success', 'message': 'Report approved'})
    else:
        # return a message
        return jsonify({'error': 'failed', 'message': 'Report not found'})

# to reopen the violation
@system_admin_api.route('/reopen-removedviolation', methods={'POST'})
def reopenRemoveViolations():
     # Assuming the incoming data is JSON
    data = request.get_json()
    # Extract incidentId from the JSON payload
    violation_id = data.get('ViolationId')
    # Your logic to handle the incidentId
    print('Received ViolationId:', violation_id)
    # make a querry calling the incidentreport table
    violation = ViolationForm.query.filter_by(ViolationId=violation_id).first()
    # if the incident is found
    if violation:
        # change the status to approved
        violation.Status = 'pending'
        # commit the changes
        db.session.commit()
        # return a message
        return jsonify({'result': 'success', 'message': 'Report approved'})
    else:
        # return a message
        return jsonify({'error': 'failed', 'message': 'Report not found'})

# to maanage the violation using the modal
@system_admin_api.route('/manage-violation-offense', methods={'POST'})
def manageViolationOffense():
    # Assuming the incoming data is JSON
    data = request.get_json()
    # Extract ViolationId and new status from the JSON payload
    violation_id = data.get('ViolationId')
    new_status = data.get('newStatus')

    # Fetch the violation from the ViolationForm table
    violation = ViolationForm.query.filter_by(ViolationId=violation_id).first()

    # If violation is found, extract IncidentId
    if violation:
        incident_id = violation.IncidentId

        # Fetch the incident type from the IncidentType table based on IncidentId
        incident_type = IncidentType.query.filter_by(IncidentTypeId=incident_id).first()

        # If the incident type is found, extract relevant data
        if incident_type:
            excused = incident_type.Excused
            one_offense = incident_type.OneOffense
            two_offense = incident_type.TwoOffense
            three_offense = incident_type.ThreeOffense
            four_offense = incident_type.FourOffense

            # Update the status of the violation if it exists
            violation.Status = new_status
            db.session.commit()  # Commit the changes
            return jsonify({'result': 'success', 'message': 'Report approved'})
        else:
            return jsonify({'error': 'failed', 'message': 'Incident type not found'})
    else:
        return jsonify({'error': 'failed', 'message': 'Violation not found'})

@system_admin_api.route('/get-violation-type/<int:ViolationId>', methods={'GET'})
def getViolationType(ViolationId):
    #fetch the violation type
    violation_type = db.session.query(ViolationForm, IncidentType).join(IncidentType, IncidentType.IncidentTypeId == ViolationForm.IncidentId).filter(ViolationForm.ViolationId == ViolationId).first()
    dict_violationoffense = {}
    if violation_type.IncidentType.Excused:
        dict_violationoffense['Excused'] = violation_type.IncidentType.Excused
    if violation_type.IncidentType.OneOffense:
        dict_violationoffense['1st Offense'] = violation_type.IncidentType.OneOffense
    if violation_type.IncidentType.TwoOffense:
        dict_violationoffense['2nd Offense'] = violation_type.IncidentType.TwoOffense
    if violation_type.IncidentType.ThreeOffense:
        dict_violationoffense['3rd Offense'] = violation_type.IncidentType.ThreeOffense
    if violation_type.IncidentType.FourOffense:
        dict_violationoffense['4th Offense'] = violation_type.IncidentType.FourOffense
    return jsonify({'result': dict_violationoffense})

 
# to assign investigator on cases
@system_admin_api.route('/assign-faculty', methods=['POST'])
def assignFaculty():
    try:
        # Check if the form data includes a file
        if 'file' not in request.files:
            return jsonify({'error': 'failed', 'message': 'No file part'})

        file = request.files['file']

        # Validate that the file is a PDF
        if file.filename == '':
            return jsonify({'error': 'failed', 'message': 'No selected file'})

        if file and not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'failed', 'message': 'Invalid file type. Only PDFs are allowed'})

        # Read file data
        file_data = file.read()

        # Assuming the other incoming data is in form data format
        incident_id = request.form.get('incidentId')
        assigned_faculty = request.form.get('assignedFaculty')

        # Query the incident report
        report = IncidentReport.query.filter_by(Id=incident_id).first()

        # Check if the incident report is found
        if report:
            # Update InvestigatorId with assigned_faculty
            report.InvestigatorId = assigned_faculty
            # Change the status to approved
            report.IsAccessible = True
            # Update InitialAssessmentName and InitialAssessmentData
            report.InitialAssessmentName = file.filename
            report.InitialAssessmentData = file_data

            # Commit the changes to the database
            db.session.commit()

            try:
                # Compose the email message
                msg = Message(
                    'Notification of Case Assignment: Investigation of Student Matter',
                    sender=("SCDS", "scdspupqc.edu@gmail.com"),
                    recipients=['david.ilustre@gmail.com']
                )
                msg.html = render_template('email_templates/faculty_notyf_case.html', caseId=incident_id)
                # Send the email
                mail.send(msg)
                # Return a success response
                return jsonify({'result': 'success', 'message': 'Faculty assigned, case approved, and email notification sent'})
            except Exception as e:
                # Log the exception and return an error response
                print('An error occurred while sending the email notification:', e)
                return jsonify({'error': 'failed', 'message': 'Faculty assigned, case approved, but email notification failed'}), 500
        else:
            # Return an error message if the incident report is not found
            return jsonify({'error': 'failed', 'message': 'Report not found'})
    except Exception as e:
        # Return an error message if an exception occurs
        print('error', e)
        return jsonify({'error': 'failed', 'message': str(e)})



@system_admin_api.route('/manage-sanction', methods={'POST'})
def manageSanction():
    try:
        # Assuming the incoming data is JSON
        data = request.get_json()
        # Extract incidentId and assignedFaculty from the JSON payload
        incident_id = data.get('incidentId')
        print('Received incidentId:', incident_id)
        
        manage_sanction = data.get('manageSanction')
        print('Received Sanction:', manage_sanction)

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


@system_admin_api.route('/cases-overview', methods=['GET'])
def cases_overview():
    try:
        # Get the count of total pending cases
        total_pending_cases = IncidentReport.query.filter_by(status='pending').count()

        # Get the count of resolved cases
        resolved_cases = IncidentReport.query.filter_by(status='approved').count()

        # Calculate the violation rate (assuming total number of cases is available)
        total_cases = total_pending_cases + resolved_cases
        if total_cases > 0:
            violation_rate = (total_pending_cases / total_cases) * 100
        else:
            violation_rate = 0

        # Get the details of the latest case (assuming the IncidentReport table has a 'created_at' field)
        latest_case = IncidentReport.query.order_by(IncidentReport.created_at.desc()).first()

        # Construct the response dictionary
        response = {
            'latestCase': {
                'date': latest_case.created_at.strftime('%Y-%m-%d'),
                'description': latest_case.description,
                # Add more fields if needed
            },
            'totalPending': total_pending_cases,
            'resolvedCases': resolved_cases,
            'violationRate': violation_rate
        }

        return jsonify(response), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch cases overview', 'message': str(e)}), 500
    

@system_admin_api.route('/total-pending-case', methods=['GET'])
def totalPendingCase():
    totalPendingCase = db.session.query(func.count(IncidentReport.Id)).filter(IncidentReport.Status == 'pending').scalar()

    return jsonify(totalPendingCase)  # Return the result as JSON


@system_admin_api.route('/total-pending-faculty-case', methods=['GET'])
def totalPendingFacultyCase():
    totalPendingFacultyCase = db.session.query(func.count(FacultyIncidentReport.Id)).filter(FacultyIncidentReport.Status == 'pending').scalar()

    return jsonify(totalPendingFacultyCase)  # Return the result as JSON

@system_admin_api.route('/total-pending-violation', methods=['GET'])
def totalPendingViolation():
    totalPendingViolation = db.session.query(func.count(ViolationForm.ViolationId)).filter(ViolationForm.IsAccessible == False).scalar()
    
    return jsonify(totalPendingViolation)  # Return the result as JSON

    
@system_admin_api.route('/total-resolved-case', methods=['GET'])
def totalResolvedCase():
    totalResolvedCase = db.session.query(func.count(IncidentReport.Id)).filter(IncidentReport.Status == 'approved').scalar()

    return jsonify(totalResolvedCase)  # Return the result as JSON

@system_admin_api.route('/total-resolved-violation', methods=['GET'])
def totalResolvedViolation():
    totalResolvedViolation = db.session.query(func.count(ViolationForm.ViolationId)).filter(ViolationForm.IsAccessible == True).scalar()
    

    return jsonify(totalResolvedViolation)

@system_admin_api.route('/violation-rate', methods=['GET'])
def violationRate():
    totalPendingCase = db.session.query(IncidentReport).filter(IncidentReport.Status == 'pending').count()
    totalResolvedCase = db.session.query(IncidentReport).filter(IncidentReport.Status != 'pending').count()
    totalPendingViolation = db.session.query(ViolationForm).filter(ViolationForm.IsAccessible == False, ViolationForm.Status == 'pending').count()
    totalResolvedViolation = db.session.query(ViolationForm).filter(ViolationForm.IsAccessible == True, ViolationForm.Status != 'pending').count()
    totalCases = totalPendingCase + totalResolvedCase
    totalViolations = totalPendingViolation + totalResolvedViolation
    if totalCases > 0:
        violationRate = (totalViolations / totalCases) * 100
    else:
        violationRate = 0
    return jsonify(violationRate)