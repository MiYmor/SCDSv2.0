# api/api_routes.py
from flask import Blueprint, jsonify, request, redirect, url_for, flash, session, render_template
from models import Faculty

from werkzeug.security import check_password_hash
from decorators.auth_decorators import role_required

from .utils import updateFacultyData, getFacultyData, updatePassword, getCurrentUser

import os


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
            session['user_id'] = teacher.TeacherId
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
        json_faculty_data = getFacultyData(faculty.TeacherId)
        if json_faculty_data:
            return (json_faculty_data)
        else:
            return jsonify(message="No user data available")
    else:
        return render_template('404.html'), 404


# Update the details of the faculty
@faculty_api.route('/details/update', methods=['GET', 'POST'])
@role_required('faculty')
def updateDetails():
    faculty = getCurrentUser()
    if faculty:
        if request.method == 'POST':
            email = request.json.get('email')
            number = request.json.get('number')
            residential_address = request.json.get('residential_address')

            json_result = updateFacultyData(
                faculty.TeacherId, email, number, residential_address)

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

            json_result = updatePassword(faculty.TeacherId, password, new_password, confirm_password)

            return json_result

        else:
            flash('Invalid email or password', 'danger')
            return redirect(url_for('facultyLogin'))
    else:
        return render_template('404.html'), 404

