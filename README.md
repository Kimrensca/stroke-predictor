# Stroke Predictor Web App

A Flask web application that predicts the risk of stroke based on user input.

## 🚀 Features

- User registration and login
- Secure password hashing
- Forgot password with email reset
- Predict stroke risk using a trained XGBoost model
- Save prediction history for each user
- Bootstrap UI for a modern interface

## 🛠 Technologies Used

- Python
- Flask
- SQLAlchemy
- Flask-Login
- Flask-Mail
- Bootstrap
- XGBoost
- SQLite

## 📦 Installation

1. **Clone the repository:**

```bash
git clone https://github.com/yourusername/stroke-predictor.git
cd stroke-predictor

2. **Create a virtual environment:**
python -m venv venv

3. **Activate the virtuel environment:**
        Windows:
            venv\Scripts\activate
            
        macOS/Linux:
            source venv/bin/activate

4. **Install dependencies:**
    pip install -r requirements.txt

5. ** Create a .env file:**
SECRET_KEY=your_secret_key_here
SQLALCHEMY_DATABASE_URI=sqlite:///instance/stroke_app.db
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_email_password_or_app_password

6. ** Initialize the database:**
python create_db.py

7. ** Run the application:**
flask run

Or run via:
  python app.py

Or for production:
gunicorn app:app

 ✨ Using the App
Visit the home page and register a new account.

Log in with your credentials.

Fill out the prediction form to get your stroke risk analysis.

View your past predictions on the History page.

Forgot your password? Request a password reset link via email.

🔗 Deployment
This app can be deployed on:

Render

Heroku

Hugging Face Spaces

Other platforms supporting Python and WSGI servers

## 📸 Screenshots

### 🔑 Login Page
![Login](static/screenshots/login.png)

### 📝 Register Page
![Register](static/screenshots/register.png)

### ✉️ Forgot Password Page
![Forgot Password](static/screenshots/forgot_password.png)

### 🏠 Home Page
![Home](static/screenshots/home.png)

### ⚙️ Prediction Form

**Prediction Form - Part 1**  
![Prediction Form 1](static/screenshots/predict_form.png)

**Prediction Form - Part 2**  
![Prediction Form 2](static/screenshots/predict_form2.png)

**Prediction Form - Part 3**  
![Prediction Form 3](static/screenshots/predict_form3.png)

### ✅ Prediction Result
![Result](static/screenshots/result.png)

### 🕓 Prediction History
![History](static/screenshots/history.png)



👤 Author
Caren

GitHub: Kimrensca

Email: rensca35@gmail.com

📜 License
This project is licensed under the MIT License.


