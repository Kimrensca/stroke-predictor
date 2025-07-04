from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from flask import flash
from sqlalchemy import or_
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
import joblib
import pandas as pd
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

serializer = URLSafeTimedSerializer(os.getenv('SECRET_KEY'))


# Initialize Flask app
app = Flask(__name__)

# Configure the app
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
db = SQLAlchemy(app)

# Initialize Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')
mail = Mail(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Load the saved XGBoost model
model = joblib.load('stroke_xgb_model.pkl')

# Load expected feature list
feature_names = joblib.load("stroke_xgb_features.pkl")

feature_names = [
    'age',
    'hypertension',
    'heart_disease',
    'avg_glucose_level',
    'bmi',
    'gender_Female',
    'gender_Male',
    'ever_married_No',
    'ever_married_Yes',
    'work_type_Govt_job',
    'work_type_Never_worked',
    'work_type_Private',
    'work_type_Self-employed',
    'work_type_children',
    'Residence_type_Rural',
    'Residence_type_Urban',
    'smoking_status_Unknown',
    'smoking_status_formerly smoked',
    'smoking_status_never smoked',
    'smoking_status_smokes'
]

from datetime import datetime

# User model for Flask-Login
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    reset_token = db.Column(db.String(100), nullable=True)
    token_expiry = db.Column(db.DateTime, nullable=True)

# Prediction model to store user predictions
class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    age = db.Column(db.Float)
    avg_glucose_level = db.Column(db.Float)
    bmi = db.Column(db.Float)
    hypertension = db.Column(db.Integer)
    heart_disease = db.Column(db.Integer)
    gender = db.Column(db.String(50))
    ever_married = db.Column(db.String(50))
    work_type = db.Column(db.String(50))
    residence = db.Column(db.String(50))
    smoking_status = db.Column(db.String(50))
    probability = db.Column(db.Float)
    risk_level = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Load user data for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        # Check if username or email already exists
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))
        
        # Hash the password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        new_user = User(full_name=full_name, email=email, username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_input = request.form['username']
        password = request.form['password']
        
        user = User.query.filter( or_(User.username == login_input, User.email == login_input)).first()

        # Check if user exists and password is correct
        if user and check_password_hash(user.password, password):
            remember_me = True if request.form.get("remember") else False
            login_user(user, remember=remember_me)
            session['user_id'] = user.id  # Store user ID in session
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
            return redirect(url_for('login'))
        
    return render_template('login.html')

# Route for user logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Route for password reset request
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']

        # Find user with this email
        user = User.query.filter_by(email=email).first()

        if user:
            # Generate token
            token = serializer.dumps(email, salt='password-reset-salt')

            reset_url = url_for('reset_password', token=token, _external=True)

            # Simulate sending email
            msg = Message(
                subject='Password Reset Request',
                sender = app.config['MAIL_DEFAULT_SENDER'],
                recipients=[user.email],
                body = f"""Hi {user. full_name},

                To reset your password, click the link below:

                {reset_url}

                If you did not request this, simply ignore this email.

                This link will expire in 1 hour.

                Thanks,
                Stroke Predictor Team
                """
            )
            mail.send(msg)
            # Flash success message
            flash('A password reset link has been sent to your email.', 'success')
        else:
            flash('No account found with that email.', 'danger')
            return redirect(url_for('forgot_password'))

    return render_template('forgot_password.html')

# Route for password reset
@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = serializer.loads(
            token,
            salt='password-reset-salt',
            max_age=3600  # 1 hour
        )
    except SignatureExpired:
        flash('The password reset link has expired.', 'danger')
        return redirect(url_for('forgot_password'))
    except BadSignature:
        flash('Invalid or tampered token.', 'danger')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            user.password = generate_password_hash(new_password)
            db.session.commit()
            flash('Your password has been reset. Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('User not found.', 'danger')
            return redirect(url_for('forgot_password'))

    return render_template('reset_password.html', token=token)

@app.route('/send-test-email')
def send_test_email():
    msg = Message(
        subject='Hello from Stroke Predictor Web App!',
        recipients=[os.getenv('MAIL_USERNAME')],
        body='This is a test email to verify that Flask-Mail is working correctly.'
    )
    mail.send(msg)
    print("EMAIL USER:", os.getenv('MAIL_USERNAME'))
    print("EMAIL PASSWORD:", os.getenv('MAIL_PASSWORD'))
    return 'Email sent!'

@app.route('/')
@login_required
def home():
    return render_template('home.html')

@app.route('/predict-form', methods=['GET'])
@login_required
def predict_form():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
@login_required
def predict():
    # Grab inputs
    age = float(request.form["age"])
    avg_glucose_level = float(request.form["avg_glucose_level"])
    bmi = float(request.form["bmi"])
    hypertension = int(request.form["hypertension"])
    heart_disease = int(request.form["heart_disease"])

    # Categorical mappings
    gender = request.form["gender"]
    ever_married = request.form["ever_married"]
    work_type = request.form["work_type"]
    residence = request.form["Residence_type"]
    smoking_status = request.form["smoking_status"]

    # Initialize all feature columns with 0
    data = dict.fromkeys(feature_names, 0)

    # Assign numeric fields
    data["age"] = age
    data["avg_glucose_level"] = avg_glucose_level
    data["bmi"] = bmi
    data["hypertension"] = hypertension
    data["heart_disease"] = heart_disease

    # One-hot encodings
    data[f"gender_{gender}"] = 1
    data[f"ever_married_{ever_married}"] = 1
    data[f"work_type_{work_type}"] = 1
    data[f"Residence_type_{residence}"] = 1
    data[f"smoking_status_{smoking_status}"] = 1

    # Convert to DataFrame
    X_input = pd.DataFrame([data])

    # Predict
    prob = float(model.predict_proba(X_input)[0][1])
    threshold = 0.40
    prediction_flag = int(prob >= threshold)

    # Determine risk category
    if prob < 0.4:
        risk_level = "Low"
        alert_class = "success"
        risk_message = "Our model predicts a low risk of stroke."
        recommendations = [
        "✅ Maintain your healthy lifestyle.",
        "Maintain a healthy diet rich in fruits, vegetables, and whole grains.",
        "Exercise regularly to keep your heart and blood vessels strong.",
        "Monitor your blood pressure, cholesterol, and glucose levels.",
        "Avoid smoking and limit alcohol consumption.",
        "Stay hydrated and manage stress effectively."
    ]
    elif prob < 0.6:
        risk_level = "Moderate"
        alert_class = "warning"
        risk_message = "Our model predicts a moderate risk of stroke. Please consider discussing this with your doctor."
        recommendations = [
        "⚠️  Adopt a healthy lifestyle.",
        "Consult your doctor about your risk factors and prevention strategies.",
        "Manage chronic conditions like hypertension, diabetes, or high cholesterol.",
        "Adopt a balanced diet low in salt and saturated fats.",
        "Increase physical activity and maintain a healthy weight.",
        "Limit alcohol intake and avoid smoking.",
        "Consider regular health check-ups to monitor your condition."
        
        ]
    else:
        risk_level = "High"
        alert_class = "danger"
        risk_message = "Our model predicts a high risk of stroke. Please consult a healthcare professional."
        recommendations = [
        "🚨 Seek medical evaluation as soon as possible for a full assessment.",
        "Strictly manage conditions like hypertension, diabetes, or heart disease.",
        "Avoid smoking entirely and limit alcohol consumption.",
        "Adopt a heart-healthy diet and reduce stress where possible.",
        "Engage in regular physical activity as advised by your healthcare provider.",
        "Consider regular check-ups to monitor your health status."
        ]

    # Save prediction to database
    new_pred = Prediction(
        user_id=current_user.id,
        age=age,
        avg_glucose_level=avg_glucose_level,
        bmi=bmi,
        hypertension=hypertension,
        heart_disease=heart_disease,
        gender=gender,
        ever_married=ever_married,
        work_type=work_type,
        residence=residence,
        smoking_status=smoking_status,
        probability=prob,
        risk_level=risk_level
    )
    db.session.add(new_pred)
    db.session.commit()

    flash('Prediction saved successfully! You can view your prediction history anytime.', 'success')

    # Render result template
    return render_template(
        "result.html",
        risk_level = risk_level,
        probability = f"{prob * 100:.1f}%",
        alert_class = alert_class,
        risk_message = risk_message,
        recommendations = recommendations,
        prediction_flag = prediction_flag
        
    )

@app.route('/history')
@login_required
def history():
    # Fetch user's prediction history
    predictions = Prediction.query.filter_by(user_id=current_user.id).all()
    return render_template('history.html', predictions=predictions)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404



if __name__ == "__main__":
    app.run(debug=True)
