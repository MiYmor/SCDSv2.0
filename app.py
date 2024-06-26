
from flask import Flask, render_template, redirect, url_for, session, request, flash, get_flashed_messages
from flask_caching import Cache
from flask_cors import CORS
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired
from flask_mail import Mail, Message



from Api.v1.student.api_routes import student_api
from Api.v1.faculty.api_routes import faculty_api
from Api.v1.systemadmin.api_routes import system_admin_api

import os
from dotenv import load_dotenv

from models import init_db, IncidentReport, IncidentType, Location, db
from models import Student, Faculty, SystemAdmin, IncidentType, Location, IncidentReport
from flask_jwt_extended import JWTManager

from decorators.auth_decorators import preventAuthenticated, role_required
from datetime import  timedelta
from mail import mail  # Import mail from the mail.py module


def create_app():
    load_dotenv()  # Load environment variables from .env file
    app = Flask(__name__)

    if __name__ == '__main__':
        app = create_app()
        app.run(debug=True)

    app.config['WTF_CSRF_ENABLED'] = False
    # SETUP YOUR POSTGRE DATABASE HERE
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    
    # Configure Flask to use HTTPS
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # or 'Strict'
    app.config['SESSION_PERMANENT'] = True
    
    # Replace 'your-secret-key' with an actual secret key
    app.secret_key = os.getenv('SECRET_KEY')
    Cache(app, config={'CACHE_TYPE': 'simple'})
    # cache.init_app(app)

    # Allowed third party apps
    allowed_origins = ["*"]
    CORS(app, origins=allowed_origins, allow_headers=["Authorization", "X-API-Key"])

    jwt = JWTManager(app)
    init_db(app)
    
   
    # Configure Flask-Mail for sending emails
    app.config['MAIL_SERVER'] = os.getenv('SCDS_MAIL_SERVER')
    app.config['MAIL_PORT'] = os.getenv('SCDS_MAIL_PORT')
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USERNAME'] = os.getenv('SCDS_MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('SCDS_MAIL_PASSWORD')
    mail = Mail(app)
    # app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
    mail.init_app(app)
    
    app.config['UPLOAD_FOLDER'] = 'path/to/upload/folder'

    # The Api Key is static for development mode. The Api key in future must refresh in order to secure the api endpoint of the application
    # student_api_key = os.getenv('STUDENT_API_KEY')
    # faculty_api_key = os.getenv('FACULTY_API_KEY')
    # system_admin_api_key = os.getenv('SYSTEM_ADMIN_API_KEY')

    # The api base url for api endpoints
    student_api_base_url = os.getenv('STUDENT_API_BASE_URL')
    faculty_api_base_url = os.getenv('FACULTY_API_BASE_URL')
    system_admin_api_base_url = os.getenv('SYSTEM_ADMIN_API_BASE_URL')
    

    @app.context_processor
    def custom_context_processor():
        authenticated = False
        if 'user_role' in session:
            authenticated = True
        return {'authenticated': authenticated}
    
    @app.before_request
    def before_request():
        if 'user_role' in session:
            print(session['user_role'])
        session.permanent=True
        pass
    
    # ===========================================================================
    # ROUTING FOR THE APPLICATION (http:localhost:3000)

    @app.route('/practice')
    def practice():
        return render_template('practice.html')



    @app.route('/')
    @preventAuthenticated
    def home():
        return render_template('main/index.html')

    @app.route('/case-filing')
    @preventAuthenticated
    def fileCase():
        return render_template('main/index_case.html')
    
    @app.route('/case-manage')
    @preventAuthenticated
    def manageCase():
        return render_template('main/index_manage.html')

    @app.route('/logout')
    def logout():
        session.clear()
        if 'user_role' in session:
            print(session['user_role'])
        else :
            print("no user role")
        return redirect(url_for('home'))  # Redirect to home or appropriate route

    # ========================================================================
    # ALL STUDENT ROUTES HERE
    @app.route('/student')
    @preventAuthenticated
    def studentLogin():
        return render_template('student/login.html')
    

    @app.route('/student/reset-request')
    @preventAuthenticated
    def studentResetRequest():
        return render_template('student/reset_password_request.html', student_api_base_url=student_api_base_url)


    @app.route('/student/home')
    @role_required('student')
    def studentHome():
        return render_template('student/home.html', student_api_base_url=student_api_base_url, current_page="home")


    @app.route('/student/profile')
    @role_required('student')
    def studentProfile():
        return render_template('student/profile.html', student_api_base_url=student_api_base_url, current_page="profile")


    @app.route('/student/change-password')
    @role_required('student')
    def changePassword():
        return render_template('student/change_password.html', student_api_base_url=student_api_base_url,  current_page="change-password")

    @app.route('/student/view-cases')
    @role_required('student')
    def studentViewCases():
        reports = IncidentReport.query.all()
        return render_template('student/view_reports.html', reports=reports, student_api_base_url=student_api_base_url,  current_page="view-cases")

    @app.route('/student/view-violations')
    @role_required('student')
    def studentViewViolations():
        reports = IncidentReport.query.all()
        return render_template('student/view_violations.html', reports=reports, student_api_base_url=student_api_base_url,  current_page="view-violations")
    
    @app.route('/student/incident-report', methods=['GET'])
    @role_required('student')
    def studentIncidentReport():
        # Fetch incident types and locations from the database
        locations = Location.query.all()
        # Fetch the list of students (modify the query based on your data model)
        students = Student.query.all()
        # Pass the 'authenticated' variable, students, incident types, and locations to the template context
        return render_template('student/incident_report_form.html', authenticated=True, students=students, locations=locations, current_page="incident-report")
    
    @app.route('/student/faculty-incident-report', methods=['GET'])
    @role_required('student')
    def facultyIncidentReport():
        # Fetch incident types and locations from the database
        locations = Location.query.all()
        faculty  = Faculty.query.all()
        # Pass the 'authenticated' variable, students, incident types, and locations to the template context
        return render_template('student/faculty_case.html', authenticated=True, locations=locations, faculty=faculty , current_page="faculty-incident-report")
    
    

    # ========================================================================
    # ALL FACULTY ROUTES HERE
    @app.route('/faculty')
    @preventAuthenticated
    def facultyLogin():
        return render_template('faculty/login.html')
    
    @app.route('/sdb')
    @preventAuthenticated
    def sdbLogin():
        return render_template('faculty/login_sdb.html')
    
    @app.route('/sdb/dashboard')
    @role_required('faculty')
    def sdbHome():
        return render_template('faculty/dashboard_sdb.html', faculty_api_base_url=faculty_api_base_url, current_page="sdb-dashboard")


    @app.route('/faculty/dashboard')
    @role_required('faculty')
    def facultyHome():
        return render_template('faculty/dashboard.html', faculty_api_base_url=faculty_api_base_url, current_page="dashboard")


    @app.route('/faculty/profile')
    @role_required('faculty')
    def facultyProfile():
        return render_template('faculty/profile.html', faculty_api_base_url=faculty_api_base_url, current_page="profile")
    
    @app.route('/faculty/violation-form', methods=['GET'])
    @role_required('faculty')
    def violationFOrm():
        # Fetch incident types and locations from the database
        incident_types = IncidentType.query.all()
        locations = Location.query.all()
        # Fetch the list of students (modify the query based on your data model)
        students = Student.query.all()
        faculty = Faculty.query.all()
        # Pass the 'authenticated' variable, students, incident types, and locations to the template context
        return render_template('faculty/violation_form.html', authenticated=True, students=students, incident_types=incident_types, locations=locations,faculty=faculty, current_page="violation-form")
    
    @app.route('/faculty/manage-reports')
    @role_required('faculty')
    def reportManagement():
        return render_template('faculty/manage_report.html', faculty_api_base_url=faculty_api_base_url, current_page="manage-reports")
    
    @app.route('/faculty/approved-reports')
    @role_required('faculty')
    def approvedReports():
        return render_template('faculty/approved_report.html', faculty_api_base_url=faculty_api_base_url, current_page="approved-reports")

    @app.route('/faculty/change-password')
    @role_required('faculty')
    def facultyChangePassword():
        return render_template('faculty/change_password.html', faculty_api_base_url=faculty_api_base_url, current_page="change-password")

    # ========================================================================
    # ALL SYSTEM ADMIN ROUTES HERE
    @app.route('/system-admin')
    @preventAuthenticated
    def systemAdminLogin():
        return render_template('systemadmin/login.html')

    @app.route('/system-admin/home')
    @role_required('systemAdmin')
    def systemAdminHome():
        return render_template('systemadmin/home.html', system_admin_api_base_url=system_admin_api_base_url, current_page="home")
    
    # ========================================================================
    # All Student Case Routes Here
    @app.route('/systemadmin/manage-reports')
    @role_required('systemAdmin')
    def reportManagementAdmin():
        #fetch the list of faculty
        faculty = Faculty.query.all()
        return render_template('systemadmin/manage_report.html', system_admin_api_base_url=system_admin_api_base_url,faculty=faculty, current_page="manage-reports")
    
    @app.route('/systemadmin/close-case')
    @role_required('systemAdmin')
    def closedCase():
        return render_template('systemadmin/closed_case.html', system_admin_api_base_url=system_admin_api_base_url, current_page="close-case")
    
    @app.route('/systemadmin/resolved-case')
    @role_required('systemAdmin')
    def resolvedCase():
        return render_template('systemadmin/resolved_case.html', system_admin_api_base_url=system_admin_api_base_url, current_page="resolved-case")
    
    @app.route('/systemadmin/resolved-precase')
    @role_required('systemAdmin')
    def resolvedprecase():
        return render_template('systemadmin/resolve_precase.html', system_admin_api_base_url=system_admin_api_base_url, current_page="resolved-precase")
    
    # ========================================================================
    # All Faculty Case Routes Here
    @app.route('/systemadmin/manage-faculty-case')
    @role_required('systemAdmin')
    def facultyReportManagementAdmin():
        #fetch the list of faculty
        return render_template('systemadmin/manage_faculty_case.html', system_admin_api_base_url=system_admin_api_base_url, current_page="manage-faculty-case")
    
    @app.route('/systemadmin/resolved-faculty-case')
    @role_required('systemAdmin')
    def resolvedFacultyCase():
        #fetch the list of faculty
        return render_template('systemadmin/resolved_faculty_case.html', system_admin_api_base_url=system_admin_api_base_url, current_page="resolved-faculty-case")
    
    @app.route('/systemadmin/removed-faculty-case')
    @role_required('systemAdmin')
    def removedFacultyCase():
        #fetch the list of faculty
        return render_template('systemadmin/removed_faculty_case.html', system_admin_api_base_url=system_admin_api_base_url, current_page="removed-faculty-case")
    
    # ========================================================================
    # All Violation Routes Here
    @app.route('/systemadmin/manage-violations')
    @role_required('systemAdmin')
    def violationManagementAdmin():
        #fetch the list of offense per violation type
        violation_type = IncidentType.query.all()
        return render_template('systemadmin/manage_violation.html', system_admin_api_base_url=system_admin_api_base_url,violation_type=violation_type, current_page="manage-violations")
    
    @app.route('/systemadmin/close-violation')
    @role_required('systemAdmin')
    def closedViolation():
        return render_template('systemadmin/closed_violation.html', system_admin_api_base_url=system_admin_api_base_url, current_page="close-violation")
    
    @app.route('/systemadmin/removed-violation')
    @role_required('systemAdmin')
    def removedViolation():
        return render_template('systemadmin/removed_violation.html', system_admin_api_base_url=system_admin_api_base_url, current_page="removed-violation")
    # ========================================================================
    # Register the API blueprint
    app.register_blueprint(system_admin_api, url_prefix=system_admin_api_base_url)
    app.register_blueprint(faculty_api, url_prefix=faculty_api_base_url)
    app.register_blueprint(student_api, url_prefix=student_api_base_url)


    @app.route('/page_not_found')  # Define an actual route
    def page_not_found():
        return handle_404_error(None)


    @app.errorhandler(404)
    def handle_404_error(e):
        return render_template('404.html'), 404

    return app


    