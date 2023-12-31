
from flask import Flask, render_template, redirect, url_for, session, request
from flask_caching import Cache
from flask_cors import CORS
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired


from Api.v1.student.api_routes import student_api
from Api.v1.faculty.api_routes import faculty_api
from Api.v1.systemadmin.api_routes import system_admin_api

from flask_mail import Mail, Message
import os
from dotenv import load_dotenv

from models import init_db, IncidentReport, IncidentType, Location, db
from models import Student, Faculty, SystemAdmin, IncidentType, Location, IncidentReport
from flask_jwt_extended import JWTManager

from decorators.auth_decorators import preventAuthenticated, role_required
from datetime import  timedelta
from mail import mail  # Import mail from the mail.py module

class IncidentReportForm(FlaskForm):
    date = StringField('Date', validators=[DataRequired()])
    time = StringField('Time', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    parties_involved = StringField('Parties Involved')
    description = TextAreaField('Description', validators=[DataRequired()])


def create_app():
    load_dotenv()  # Load environment variables from .env file
    app = Flask(__name__)

    if __name__ == '__main__':
        app.run(debug=True)
    
    # SETUP YOUR POSTGRE DATABASE HERE
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    
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
    app.config['MAIL_SERVER'] =  os.getenv("MAIL_SERVER")
    app.config['MAIL_PORT'] =  os.getenv("MAIL_PORT")
    app.config['MAIL_USERNAME'] =  os.getenv("MAIL_USERNAME")
    app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    # app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
    mail.init_app(app)
    # The Api Key is static for development mode. The Api key in future must refresh in order to secure the api endpoint of the application
    # student_api_key = os.getenv('STUDENT_API_KEY')
    # faculty_api_key = os.getenv('FACULTY_API_KEY')
    # system_admin_api_key = os.getenv('SYSTEM_ADMIN_API_KEY')

    # The api base url for api endpoints
    student_api_base_url = os.getenv("STUDENT_API_BASE_URL")
    faculty_api_base_url = os.getenv("FACULTY_API_BASE_URL")
    system_admin_api_base_url = os.getenv("SYSTEM_ADMIN_API_BASE_URL")

    @app.context_processor
    def custom_context_processor():
        authenticated = False
        if 'user_role' in session:
            authenticated = True
        return {'authenticated': authenticated}
    
    @app.before_request
    def before_request():
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


    @app.route('/logout')
    def logout():

        session.clear()
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
    
    #old code might be useful down the road
    # @app.route('/student/incident-report', methods=['GET', 'POST'])
    # def studentIncidentReport():
    #     return render_template('student/incident_report_form.html', student_api_base_url=student_api_base_url,  current_page="incident-report")


    @app.route('/student/view-reports')
    def studentViewReports():
        reports = IncidentReport.query.all()
        return render_template('student/view_reports.html', reports=reports, student_api_base_url=student_api_base_url,  current_page="view-reports")

    
    @app.route('/student/incident-report', methods=['GET'])
    def studentIncidentReport():
        # Fetch incident types and locations from the database
        incident_types = IncidentType.query.all()
        locations = Location.query.all()
        # Fetch the list of students (modify the query based on your data model)
        students = Student.query.all()
        # Pass the 'authenticated' variable, students, incident types, and locations to the template context
        return render_template('student/incident_report_form.html', authenticated=True, students=students, incident_types=incident_types, locations=locations, current_page="incident-report")

    # ========================================================================


    # ALL FACULTY ROUTES HERE
    @app.route('/faculty')
    @preventAuthenticated
    def facultyLogin():
        return render_template('faculty/login.html')


    @app.route('/faculty/dashboard')
    @role_required('faculty')
    def facultyHome():
        return render_template('faculty/dashboard.html', faculty_api_base_url=faculty_api_base_url, current_page="dashboard")


    @app.route('/faculty/profile')
    @role_required('faculty')
    def facultyProfile():
        return render_template('faculty/profile.html', faculty_api_base_url=faculty_api_base_url, current_page="profile")
    
    @app.route('/faculty/manage-reports')
    @role_required('faculty')
    def reportManagement():
        return render_template('faculty/manage_report.html', faculty_api_base_url=faculty_api_base_url, current_page="manage-reports")

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
    
    @app.route('/systemadmin/manage-reports')
    @role_required('systemAdmin')
    def reportManagementAdmin():
        return render_template('systemadmin/manage_report.html', system_admin_api_base_url=system_admin_api_base_url, current_page="manage-reports")
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


    