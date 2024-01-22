from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from flask_login import UserMixin
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.dialects.postgresql import ARRAY
import os

import time
from datetime import datetime
from sqlalchemy import text

from flask_sqlalchemy import SQLAlchemy

# from data.admins import faculty_data
# from data.users import student_data
# from data.superadmin import system_admin_data
# from data.incidenttype import incidenttype_data
# from data.location import location_data


db = SQLAlchemy()

class Location(db.Model):
    __tablename__ = 'SCDSLocation'
    
    LocationId = db.Column(db.Integer, primary_key=True, autoincrement=True) #LocationID
    Name = db.Column(db.String(100), nullable=False) #LocationName
    
    def to_dict(self):
        return {
            'Name': self.name,
        }
        
class IncidentType(db.Model):
    __tablename__ = 'SCDSIncidentType'
    
    IncidentTypeId = db.Column(db.Integer, primary_key=True, autoincrement=True) #IncidentTypeID
    Name = db.Column(db.String(100), nullable=False) #IncidentName
    
    def to_dict(self):
        return {
            'IncidentTypeId': self.IncidentTypeId,
            'Name': self.name,
        }
        
class ViolationForm(db.Model):
    __tablename__ = 'SCDSViolationForm'
    
    ViolationId = db.Column(db.Integer, primary_key=True, autoincrement=True) #ViolationFormID
    Date = db.Column(db.String(20), nullable=False) #Date
    Time = db.Column(db.String(20), nullable=False) #Time
    LocationId = db.Column(db.Integer, db.ForeignKey('SCDSLocation.LocationId', ondelete="CASCADE")) #LocationID
    StudentId = db.Column(db.Integer, db.ForeignKey('SPSStudent.StudentId', ondelete="CASCADE")) #StudentID
    IncidentId = db.Column(db.Integer, db.ForeignKey('SCDSIncidentType.IncidentTypeId', ondelete="CASCADE")) #IncidentTypeID
    ComplainantId = db.Column(db.Integer, db.ForeignKey('SPSStudent.StudentId', ondelete="CASCADE")) #ComplainantID
    Description = db.Column(db.Text, nullable=False) #Description
    Status = db.Column(db.String(20), nullable=False, default='pending') #Status
    IsAccessible = db.Column(db.Boolean, nullable=False, default=False) #IsAccessible
        
    def to_dict(self):
        return {
            'ViolationId': self.ViolationId,
            'Date': self.Date,
            'Time': self.Time,
            'LocationId': self.LocationId,
            'StudentId': self.StudentId,
            'IncidentID': self.IncidentID,
            'ComplainantID': self.ComplainantID,
            'Description': self.Description,
            'Status': self.Status,
            'IsAccessible': self.IsAccessible
        }
        
class IncidentReport(db.Model):
    __tablename__ = 'SCDSIncidentReport'
    
    Id = db.Column(db.Integer, primary_key=True, nullable=False) #ReportID
    Date = db.Column(db.String(20), nullable=False) #Date
    Time = db.Column(db.String(20), nullable=False) #Time
    IncidentId = db.Column(db.Integer, db.ForeignKey('SCDSIncidentType.IncidentTypeId', ondelete="CASCADE")) #IncidentTypeID
    LocationId = db.Column(db.Integer, db.ForeignKey('SCDSLocation.LocationId', ondelete="CASCADE")) #LocationID
    StudentId = db.Column(db.Integer, db.ForeignKey('SPSStudent.StudentId', ondelete="CASCADE")) #StudentID
    ComplainantId = db.Column(db.Integer, db.ForeignKey('SPSStudent.StudentId', ondelete="CASCADE")) #ComplainantID
    InvestigatorId = db.Column(db.Integer, db.ForeignKey('FISFaculty.FacultyId', ondelete="CASCADE"), nullable=True) #InvestigatorID
    Description = db.Column(db.Text, nullable=False) #Description
    Status = db.Column(db.String(20), nullable=False, default='pending') #Status
    IsAccessible = db.Column(db.Boolean, nullable=False, default=False) #IsAccessible
    
    def to_dict(self):
        return {
            'Date': self.Date,
            'Time': self.Time,
            'IncidentId': self.IncidentId,
            'LocationId': self.LocationId,
            'StudentId': self.StudentId,
            'ComplainantID': self.ComplainantID,
            'InvestigatorId': self.InvestigatorId,
            'Description': self.Description,
            'Status': self.Status,
            'IsAccessible': self.IsAccessible
        }


# Student Users
class Student(db.Model): # (class SPSStudent) In DJANGO you must set the name directly here 
    __tablename__ = 'SPSStudent' # Set the name of table in database (Available for FLASK framework)

    StudentId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    StudentNumber = db.Column(db.String(30), unique=True, nullable=False)  # UserID
    FirstName = db.Column(db.String(50), nullable=False)  # First Name
    LastName = db.Column(db.String(50), nullable=False)  # Last Name
    MiddleName = db.Column(db.String(50))  # Middle Name
    Email = db.Column(db.String(50), unique=True, nullable=False)  # Email
    Password = db.Column(db.String(256), nullable=False)  # Password
    Gender = db.Column(db.Integer, nullable=True)  # Gender
    DateOfBirth = db.Column(db.Date)  # DateOfBirth
    PlaceOfBirth = db.Column(db.String(50))  # PlaceOfBirth
    ResidentialAddress = db.Column(db.String(50))  # ResidentialAddress
    MobileNumber = db.Column(db.String(11))  # MobileNumber
    IsOfficer = db.Column(db.Boolean, default=False)
    Token = db.Column(db.String(128))  # This is for handling reset password 
    TokenExpiration = db.Column(db.DateTime) # This is for handling reset password 
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    # IsBridging
    
    def to_dict(self):
        return {
            'StudentId': self.StudentId,
            'StudentNumber': self.StudentNumber,
            'FirstName': self.FirstName,
            'LastName': self.LastName,
            'MiddleName': self.MiddleName,
            'Email': self.Email,
            'Password': self.Password,
            'Gender': self.Gender,
            'DateOfBirth': self.DateOfBirth,
            'PlaceOfBirth': self.PlaceOfBirth,
            'ResidentialAddress': self.ResidentialAddress,
            'MobileNumber': self.MobileNumber,
            'IsOfficer': self.IsOfficer
        }

    def get_id(self):
        return str(self.StudentId)  # Convert to string to ensure compatibility

    def get_user_id(self):
        return self.StudentId


# Faculty Users
class Faculty(db.Model):
    __tablename__ = 'FISFaculty' # Set the name of table in database
    FacultyId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    FacultyType = db.Column(db.String(50), nullable=False)  # Faculty Type
    Rank = db.Column(db.String(50))  # Faculty Rank
    Units = db.Column(db.Numeric, nullable=False)  # Faculty Unit
    FirstName = db.Column(db.String(50), nullable=False)  # First Name
    LastName = db.Column(db.String(50), nullable=False)  # Last Name
    MiddleName = db.Column(db.String(50))  # Middle Name
    MiddleInitial = db.Column(db.String(50))  # Middle Initial
    NameExtension = db.Column(db.String(50))  # Name Extension
    BirthDate = db.Column(db.Date, nullable=False)  # Birthdate
    DateHired = db.Column(db.Date, nullable=False)  # Date Hired
    Degree = db.Column(db.String)  # Degree
    Remarks = db.Column(db.String)  # Remarks
    FacultyCode = db.Column(db.Integer, nullable=False)  # Faculty Code
    Honorific = db.Column(db.String(50))  # Honorific
    Age = db.Column(db.Numeric, nullable=False)  # Age
    
    Email = db.Column(db.String(50), unique=True, nullable=False)  # Email
    ResidentialAddress = db.Column(db.String(50))  # ResidentialAddress
    MobileNumber = db.Column(db.String(11))  # MobileNumber
    Gender = db.Column(db.Integer) # Gender # 1 if Male 2 if Female
    
    Password = db.Column(db.String(256), nullable=False)  # Password
    ProfilePic= db.Column(db.String(50),default="14wkc8rPgd8NcrqFoRFO_CNyrJ7nhmU08")  # Profile Pic
    IsActive = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    # FOREIGN TABLES
    

    def to_dict(self):
        return {
            'faculty_account_id': self.FacultyId,
            'faculty_type': self.FacultyType,
            'rank': self.Rank,
            'units': self.Units,
            'first_name': self.FirstName,
            'last_name': self.LastName,
            'middle_name': self.MiddleName,
            'middle_initial': self.MiddleInitial,
            'name_extension': self.NameExtension,
            'birth_date': self.BirthDate,
            'date_hired': self.DateHired,
            'degree': self.Degree,
            'remarks': self.Remarks,
            'faculty_code': self.FacultyCode,
            'honorific': self.Honorific,
            'age': self.Age,
            'email': self.Email,
            'password': self.password,
            'profile_pic': self.ProfilePic,
            'is_active': self.IsActive,
        }
        
    def get_id(self):
        return str(self.faculty_account_id)  # Convert to string to ensure compatibility

# System Admins Users
class SystemAdmin(db.Model):
    __tablename__ = 'SPSSystemAdmin'

    SysAdminId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    SysAdminNumber = db.Column(db.String(30), unique=True)  # UserID
    Name = db.Column(db.String(50), nullable=False)  # Name
    Email = db.Column(db.String(50), unique=True, nullable=False)  # Email
    Password = db.Column(db.String(256), nullable=False)  # Password
    Gender = db.Column(db.Integer)  # Gender
    DateOfBirth = db.Column(db.Date)  # DateOfBirth
    PlaceOfBirth = db.Column(db.String(50))  # PlaceOfBirth
    ResidentialAddress = db.Column(db.String(50))  # ResidentialAddress
    MobileNumber = db.Column(db.String(11))  # MobileNumber
    IsActive = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

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

    def get_user_id(self):
        return self.SysAdminId

def init_db(app):
    db.init_app(app)
#     with app.app_context():
#         inspector = inspect(db.engine)
#         if not inspector.has_table('Students'):
#             db.create_all()
#             create_sample_data()


# def create_sample_data():
#     for data in student_data:
#         student = Student(**data)
#         db.session.add(student)

#     for data in faculty_data:
#         faculty = Faculty(**data)
#         db.session.add(faculty)
        
#     for data in system_admin_data:
#         admin = SystemAdmin(**data)
#         db.session.add(admin)
        
#     for data in incidenttype_data:
#         incidenttype = IncidentType(**data)
#         db.session.add(incidenttype)
        
#     for data in location_data:
#         location = Location(**data)
#         db.session.add(location)

#     db.session.commit()
