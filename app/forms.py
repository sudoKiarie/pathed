from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError, DateTimeField, TextAreaField
from wtforms.validators import DataRequired, Email, Length
from .models import User, Doctor


class PhoneNumberForm(FlaskForm):
    """Form for submitting phone number."""
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    submit = SubmitField('Get Code')


class OTPForm(FlaskForm):
    """Form for submitting OTP code."""
    otp_code = StringField('OTP Code', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Login')


class DoctorLoginForm(FlaskForm):
    """Form for doctor login."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Login')

    def validate_email(self, email):
        """Check if the email exists in the Doctor model."""
        doctor = Doctor.query.filter_by(email=email.data).first()
        if doctor is None:
            raise ValidationError('This email is not registered. Please register first.')


class AppointmentForm(FlaskForm):
    purpose = StringField('Purpose of Appointment', validators=[DataRequired()])
    appointment_time = DateTimeField('Appointment Time', format='%Y-%m-%d %H:%M', validators=[DataRequired()])
    notes = TextAreaField('Notes')
    submit = SubmitField('Book Appointment')