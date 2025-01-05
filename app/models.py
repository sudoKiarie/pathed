# from inspect import AGEN_CLOSED
from . import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash



class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    sex = db.Column(db.String)
    age = db.Column(db.Integer)
    phone_number = db.Column(db.String)

    def __repr__(self):
        """ Format the User object"""
        return ("<User(id={}, sex={}, age={}, name={}, phone_number={})>"  # noqa: E501
                .format(self.id, self.sex, self.age,
                        self.name, self.phone_number))

class Doctor(db.Model):
    __tablename__ = 'doctor'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.String)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        """ Format the Doctor object"""
        return ("<Doctor(id={}, email={}, password_hash={}, name={}, phone_number={})>"  # noqa: E501
                .format(self.id, self.email, self.password_hash,
                        self.name, self.phone_number))



class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    appointment_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String, default="pending")
    purpose = db.Column(db.String)
    notes = db.Column(db.String)

    patient = db.relationship("User")


    def __repr__(self):
        """ Format the Appointment object"""
        return (
            "<Appointment(id={}, patient_id={}, status={}"
            "appointment_time={}, purpose={}, notes={})>"
                .format(self.id, self.patient_id, self.status,
                        self.appointment_time, self.purpose,
                        self.notes))
    


class Admin(db.Model):
    __tablename__ = 'admin'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.String)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        """ Format the Admin object"""
        return ("<Admin(id={}, email={}, password_hash={}, name={}, phone_number={})>"  # noqa: E501
                .format(self.id, self.email, self.password_hash,
                        self.name, self.phone_number))
