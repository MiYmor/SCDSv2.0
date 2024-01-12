# api/api_routes.py
from flask import Blueprint, jsonify, request, redirect, url_for, flash, session, render_template
from models import SystemAdmin, db, IncidentReport, Student, Location, IncidentType, Faculty
import pandas as pd

from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash
from decorators.auth_decorators import role_required

from .utils import getCurrentUser

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
            'Incident Type': report.incident_type,
            'Location': report.location,
            'Student': report.student,
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

@system_admin_api.route('/all-reports', methods={'GET'})
def allReports():
    print("Hello")
     #.filter = multiple queries .filter_by = single query
    allReports = db.session.query(IncidentReport, Student, Location, IncidentType).join(Student, Student.StudentId == IncidentReport.StudentId).join(Location, Location.LocationId == IncidentReport.LocationId).join(IncidentType, IncidentType.IncidentTypeId == IncidentReport.IncidentId).order_by(IncidentReport.Date).all()
    list_reports=[]
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
        return jsonify({'result': list_reports})
    
@system_admin_api.route('/access-report', methods={'POST'})
def accessReports():
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
        incident.IsAccessible = True
        # commit the changes
        db.session.commit()
        # return a message
        return jsonify({'result': 'success', 'message': 'Report approved'})
    else:
        # return a message
        return jsonify({'error': 'failed', 'message': 'Report not found'})