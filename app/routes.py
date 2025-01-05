from flask import render_template, redirect, url_for, flash, Blueprint, session, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from . import db
from datetime import datetime  # Importing datetime
from .models import User, Doctor, Appointment
from .forms import PhoneNumberForm, OTPForm, DoctorLoginForm, AppointmentForm
from werkzeug.security import check_password_hash
import os
from dotenv import load_dotenv
from openai import OpenAI

# Create the blueprint for main routes
main = Blueprint('main', __name__)



load_dotenv()

# Home route
@main.route('/')
def home():
    return render_template('home.html')

# Patient Login route
@main.route('/patient_login', methods=['GET', 'POST'])
def patient_login():
    phone_form = PhoneNumberForm()
    otp_form = OTPForm()

    # Handle phone number submission
    if not session.get('otp_sent') and phone_form.validate_on_submit() and phone_form.phone_number.data:
        phone_number = phone_form.phone_number.data

        # Simulate sending OTP (hardcoded '123456')
        generated_otp = "123456"
        flash('OTP has been sent to your phone number.', 'info')

        # Store phone number and OTP in session for the next step
        session['phone_number'] = phone_number
        session['generated_otp'] = generated_otp
        session['otp_sent'] = True


        # Redirect to allow OTP input
        return redirect(url_for('main.patient_login'))

    # Handle OTP submission
    elif session.get('otp_sent') and otp_form.validate_on_submit() and otp_form.otp_code.data:
        otp_code = otp_form.otp_code.data

        # Check if the OTP matches the session-stored value
        if otp_code == session.get('generated_otp'):
            patient = User.query.filter_by(phone_number=session.get('phone_number')).first()

            if patient:
                login_user(patient)
                
                # Clear session data after successful login
                session.pop('generated_otp', None)
                session.pop('phone_number', None)
                session.pop('otp_sent', None)

                # Debugging: successful login
                print("Login successful.")
                return redirect(url_for('main.book_appointment'))
            else:
                flash('Phone number not found. Please register first.', 'danger')
        else:
            flash('Invalid OTP. Please try again.', 'danger')

        # Debugging: failed OTP validation
        print("Failed OTP validation.")

    return render_template('patient_login.html', phone_form=phone_form, otp_form=otp_form)


# Appointment booking route
@main.route('/book_appointment', methods=['GET', 'POST'])
@login_required  # Ensure the user is logged in
def book_appointment():
    form = AppointmentForm()
    if form.validate_on_submit():
        # Here you can add logic to book the appointment (e.g., save it to the database)
        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('main.home'))  # Redirect to home or another page after booking
    return render_template('book_appointment.html', form=form)

# Function to initialize the OpenAI API client
# Initialize OpenAI client function
def initialize_openai():
    try:
        return OpenAI(
            api_key=os.getenv("API_KEY"),  # Load API key from environment
            base_url="https://api.aimlapi.com"
        )
    except Exception as e:
        print(f"Error initializing OpenAI client: {e}")
        return None

# Dynamic Questionnaire - generates next question
def dynamic_patient_questionnaire(conversation_history):
    client = initialize_openai()
    if client is None:
        return "Sorry, there was an error connecting to the AI service."

    # Create a prompt from the entire conversation history
    prompt = "\n".join(conversation_history) + "\nBased on this information, please generate the next relevant question."

    # Send the prompt to OpenAI to generate the next question
    try:
        response = client.chat.completions.create(
            model="o1-preview",  # Adjust model version as needed
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        next_question = response.choices[0].message.content.strip()
        return next_question

    except Exception as e:
        print(f"Error during OpenAI API call for next question: {e}")
        return "Sorry, there was an error generating the next question."

# Generate diagnosis based on conversation
def generate_diagnosis(conversation_history):
    client = initialize_openai()
    if client is None:
        return "Sorry, there was an error connecting to the AI service."

    # Format the conversation history into a diagnostic prompt
    prompt_for_diagnosis = "Here are the patient's responses:\n"
    for response in conversation_history:
        prompt_for_diagnosis += f"{response}\n"
    
    prompt_for_diagnosis += "Please provide 3-5 differential diagnoses along with recommended tests."

    try:
        response = client.chat.completions.create(
            model="o1-preview",
            messages=[{"role": "user", "content": prompt_for_diagnosis}],
            max_tokens=1000
        )
        diagnosis = response.choices[0].message.content.strip()
        return diagnosis

    except Exception as e:
        print(f"Error during OpenAI API call for differential diagnosis: {e}")
        return "Sorry, there was an error generating the diagnosis."

# Flask route for chatting with the AI
@main.route('/chat-with-ai', methods=['GET', 'POST'])
def chat_with_ai():
    session.permanent = True
    data = request.get_json()  # Use request.get_json() to retrieve JSON payload
    if data is None or 'msg' not in data:
        return jsonify({"error": "Invalid input"}), 400  # Handle bad input explicitly

    patient_message = data.get("msg")  # Safely get the message from the JSON payload

    if 'conversation_history' not in session:
        session['conversation_history'] = []

    # Add patient's message to the conversation history
    session['conversation_history'].append(f"Patient: {patient_message}")
    print("Conversation history:", session['conversation_history'])

    # Generate the next question using the AI
    next_question = dynamic_patient_questionnaire(session['conversation_history'])

    # Append AI's next question to the conversation history
    if next_question:
        session['conversation_history'].append(f"AI: {next_question}")

        # Return the next question to the chatbot interface
        return jsonify({'response': next_question})
    else:
        diagnosis = submit_diagnosis(session['conversation_history'])
        # Adjust the endpoint to your actual patient dashboard

        return jsonify({'response': diagnosis})

# Submit diagnosis route
def submit_diagnosis(conversation):
    # if 'conversation_history' not in session:
    #     return jsonify({'error': 'No conversation history found'}), 400
    
    # Generate diagnosis based on conversation history
    diagnosis = generate_diagnosis(conversation)

    # Clear conversation history
    conversation_notes = "\n".join(session['conversation_history'] + [f"AI: {diagnosis}"])
    
    # Extract purpose from the first question response (assuming it's the first AI response)
    purpose = session['conversation_history'][0] if session['conversation_history'] else "General Consultation"
    
    # Here, you should add logic to get the patient_id from the session or context
    patient_id = session.get('patient_id')  # Assuming patient_id is stored in the session

    # Create a new appointment entry
    new_appointment = Appointment(
        patient_id=patient_id,
        appointment_time=datetime.utcnow(),  # Set to the current time or desired time
        status="pending",  # Default status
        purpose=purpose,
        notes=conversation_notes
    )

    # Add the appointment to the database session and commit
    db.session.add(new_appointment)
    db.session.commit()

    # Clear the conversation history
    session.pop('conversation_history', None)  # Clear the conversation history
    
    # Flash a message or set session data if needed
    flash("Your appointment has been confirmed. Here are your diagnosis criteria: " + diagnosis, "success")
    # Add logic to seperate the diagnosis and recommended tests
    # The patient should only receive the recommended tests in the flash message
    

    # Redirect to the patient dashboard
    return redirect(url_for('patient_dashboard'))     

# Patient Dashboard route
@main.route('/patient_dashboard')
def patient_dashboard():
    if current_user.is_authenticated:
        return render_template('patient_dashboard.html', user=current_user)
    return redirect(url_for('main.patient_login'))

# Doctor Login route
@main.route('/doctor_login', methods=['GET', 'POST'])
def doctor_login():
    form = DoctorLoginForm()
    if form.validate_on_submit():
        email = form.email.data
        doctor = Doctor.query.filter_by(email=email).first()
        if doctor and check_password_hash(doctor.password_hash, form.password.data):
            login_user(doctor)  # Log the doctor in
            return redirect(url_for('main.doctor_dashboard'))  # Redirect to doctor dashboard
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('doctor_login.html', form=form)

# Doctor Dashboard route
@main.route('/doctor_dashboard')
@login_required
def doctor_dashboard():
    if current_user.is_authenticated:
        return render_template('doctor_dashboard.html', user=current_user)
    return redirect(url_for('main.doctor_login'))

# Logout route
@main.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))

@main.route('/reset-chat', methods=['POST'])
def reset_chat():
    session.pop('conversation_history', None)  # Remove conversation history
    return jsonify({'message': 'Conversation history cleared.'}), 200
