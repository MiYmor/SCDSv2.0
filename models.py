from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from flask_login import UserMixin
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.dialects.postgresql import ARRAY

from data.admins import faculty_data
from data.users import student_data
from data.superadmin import admin_data
from data.incidenttype import incidenttype_data
from data.location import location_data


db = SQLAlchemy()

class Location(db.Model):
    __tablename__ = 'Location'
    
    LocationId = db.Column(db.Integer, primary_key=True, autoincrement=True) #LocationID
    Name = db.Column(db.String(100), nullable=False) #LocationName
    
    def to_dict(self):
        return {
            'Name': self.name,
        }
        
class IncidentType(db.Model):
    __tablename__ = 'IncidentType'
    
    IncidentTypeId = db.Column(db.Integer, primary_key=True, autoincrement=True) #IncidentTypeID
    Name = db.Column(db.String(100), nullable=False) #IncidentName
    
    def to_dict(self):
        return {
            'IncidentTypeId': self.IncidentTypeId,
            'Name': self.name,
        }

class IncidentReport(db.Model):
    id = db.Column(db.Integer, primary_key=True) #ReportID
    date = db.Column(db.String(20), nullable=False) #Date
    time = db.Column(db.String(20), nullable=False) #Time
    IncidentId = db.Column(db.Integer, db.ForeignKey('IncidentType.IncidentTypeId', ondelete="CASCADE")) #IncidentTypeID
    LocationId = db.Column(db.Integer, db.ForeignKey('Location.LocationId', ondelete="CASCADE")) #LocationID
    StudentId = db.Column(db.Integer, db.ForeignKey('Students.StudentId', ondelete="CASCADE")) #StudentID
    description = db.Column(db.Text, nullable=False) #Description
    status = db.Column(db.String(20), nullable=False, default='pending') #Status
    is_accessible = db.Column(db.Boolean, nullable=False, default=False) #IsAccessible
    
    def to_dict(self):
        return {
            'date': self.date,
            'time': self.time,
            'IncidentId': self.IncidentId,
            'LocationId': self.LocationId,
            'StudentId': self.StudentId,
            'description': self.description,
            'status': self.status,
            'is_accessible': self.is_accessible
        }


class Student(db.Model, UserMixin):
    __tablename__ = 'Students'

    StudentId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    StudentNumber = db.Column(db.String(30), unique=True)  # UserID
    Name = db.Column(db.String(256), nullable=False)  # Name
    Email = db.Column(db.String(256), unique=True, nullable=False)  # Email
    Password = db.Column(db.String(256), nullable=False)  # Password
    Gender = db.Column(db.Integer)  # Gender
    DateOfBirth = db.Column(db.Date)  # DateOfBirth
    PlaceOfBirth = db.Column(db.String(256))  # PlaceOfBirth
    ResidentialAddress = db.Column(db.String(256))  # ResidentialAddress
    MobileNumber = db.Column(db.String(11))  # MobileNumber
    Dropout = db.Column(db.Boolean)  # Dropout
    IsGraduated = db.Column(db.Boolean, default=True)
    Token = db.Column(db.String(256))  # This field will store the reset token
    TokenExpiration = db.Column(db.DateTime)
    # IsBridging
    
    def to_dict(self):
        return {
            'StudentId': self.StudentId,
            'StudentNumber': self.StudentNumber,
            'Name': self.Name,
            'Email': self.Email,
            'Password': self.Password,
            'Gender': self.Gender,
            'DateOfBirth': self.DateOfBirth,
            'PlaceOfBirth': self.PlaceOfBirth,
            'ResidentialAddress': self.ResidentialAddress,
            'MobileNumber': self.MobileNumber,
            'Dropout': self.Dropout,
            'IsGraduated': self.IsGraduated
        }

    def get_id(self):
        return str(self.StudentId)  # Convert to string to ensure compatibility


class Faculty(db.Model, UserMixin):
    __tablename__ = 'Faculties'

    TeacherId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TeacherNumber = db.Column(db.String(30), unique=True)  # UserID
    Name = db.Column(db.String(256), nullable=False)  # Name
    Email = db.Column(db.String(256), unique=True, nullable=False)  # Email
    Password = db.Column(db.String(256), nullable=False)  # Password
    Gender = db.Column(db.Integer)  # Gender
    DateOfBirth = db.Column(db.Date)  # DateOfBirth
    PlaceOfBirth = db.Column(db.String(256))  # PlaceOfBirth
    ResidentialAddress = db.Column(db.String(256))  # ResidentialAddress
    MobileNumber = db.Column(db.String(11))  # MobileNumber
    IsActive = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'TeacherId': self.TeacherId,
            'TeacherNumber': self.TeacherNumber,
            'Name': self.Name,
            'Email': self.Email,
            'Password': self.Password,
            'Gender': self.Gender,
            'DateOfBirth': self.DateOfBirth,
            'PlaceOfBirth': self.PlaceOfBirth,
            'ResidentialAddress': self.ResidentialAddress,
            'MobileNumber': self.MobileNumber,
            'IsActive': self.IsActive
        }

    def get_id(self):
        return str(self.TeacherId)  # Convert to string to ensure compatibility

class SystemAdmin(db.Model, UserMixin):
    __tablename__ = 'SystemAdmins'

    SysAdminId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    SysAdminNumber = db.Column(db.String(30), unique=True)  # UserID
    Name = db.Column(db.String(256), nullable=False)  # Name
    Email = db.Column(db.String(256), unique=True, nullable=False)  # Email
    Password = db.Column(db.String(256), nullable=False)  # Password
    Gender = db.Column(db.Integer)  # Gender
    DateOfBirth = db.Column(db.Date)  # DateOfBirth
    PlaceOfBirth = db.Column(db.String(256))  # PlaceOfBirth
    ResidentialAddress = db.Column(db.String(256))  # ResidentialAddress
    MobileNumber = db.Column(db.String(11))  # MobileNumber
    IsActive = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'SysAdminId': self.SysAdminId,
            'SysAdminNumber': self.SysAdminNumber,
            'Name': self.Name,
            'Email': self.Email,
            'Password': self.Password,
            'Gender': self.Gender,
            'DateOfBirth': self.DateOfBirth,
            'PlaceOfBirth': self.PlaceOfBirth,
            'ResidentialAddress': self.ResidentialAddress,
            'MobileNumber': self.MobileNumber,
            'IsActive': self.IsActive
        }

    def get_id(self):
        # Convert to string to ensure compatibility
        return str(self.SysAdminId)

def init_db(app):
    db.init_app(app)
    with app.app_context():
        inspector = inspect(db.engine)
        if not inspector.has_table('Students'):
            db.create_all()
            create_sample_data()


def create_sample_data():
    for data in student_data:
        student = Student(**data)
        db.session.add(student)

    for data in faculty_data:
        faculty = Faculty(**data)
        db.session.add(faculty)
        
    for data in admin_data:
        admin = SystemAdmin(**data)
        db.session.add(admin)
        
    for data in incidenttype_data:
        incidenttype = IncidentType(**data)
        db.session.add(incidenttype)
        
    for data in location_data:
        location = Location(**data)
        db.session.add(location)

    db.session.commit()
