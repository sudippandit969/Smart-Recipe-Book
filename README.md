# 🧾 Smart Recipe Book

An intelligent, AI-powered Recipe Management Web Application built with Django. This application goes beyond simple recipe storage by integrating Google's Gemini AI to generate recipes, smart suggestions, and a community feed where users can share and review dishes.

## 🔗 Live Demo
🚀 **[View Live App on Render](https://smart-recipe-book-1.onrender.com/)**

You can register for an account to start adding your own recipes, exploring AI-generated dishes, and interacting with the community!

---

## ✨ Features

- **🧠 AI Recipe Generation:** Create brand new, creative recipes on the fly using Google's Gemini AI.
- **🔐 Secure Authentication:** Full user registration, login, and password reset functionality powered by Resend SMTP.
- **📚 Recipe Management:** Create, read, update, and delete (CRUD) your personal recipes.
- **🖼️ Image Uploads:** Attach beautiful images to your recipes.
- **🌐 Community Feed:** See recipes posted by other users, add them to your favorites, and leave ratings/feedback.
- **⭐ Favorites System:** Save recipes you love to your personal favorites list.
- **🛡️ Protected Routes:** Secure views ensuring only logged-in users can manage their data.
- **📱 Responsive UI:** Beautiful, modern interface designed to work on all devices.

---

## 🛠 Tech Stack

- **Backend:** Python, Django 5.1
- **Database:** PostgreSQL (Production on Render) / SQLite (Local Development)
- **AI Integration:** Google Generative AI (Gemini API)
- **Email Service:** Resend (SMTP for Password Resets)
- **Frontend:** HTML5, CSS3, Bootstrap 5
- **Hosting:** Render (Web Service & Managed PostgreSQL)

---

## 🚀 Local Development Setup

To run this project locally on your machine, follow these steps:

### 1. Clone the repository
```bash
git clone https://github.com/sudippandit969/Smart-Recipe-Book.git
cd Smart-Recipe-Book
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### 3. Install the dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up Environment Variables
Create a `.env` file in the root directory (or set these in your terminal) and add your API keys:
```env
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_django_secret_key
DEBUG=True
```

### 5. Run Database Migrations
```bash
python manage.py migrate
```

### 6. Start the Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000` in your browser!

---

## ☁️ Deployment (Render)

This project is configured for seamless deployment on [Render](https://render.com). 

**Required Environment Variables in Render:**
* `PYTHON_VERSION`: e.g. `3.10.0`
* `DATABASE_URL`: Internal PostgreSQL URL provided by Render.
* `SECRET_KEY`: A secure random string for Django.
* `DEBUG`: `False`
* `GEMINI_API_KEY`: Your Google Gemini API Key.
* `RESEND_API_KEY`: Your Resend API Key (for password resets).
* `DEFAULT_FROM_EMAIL`: The verified email domain for Resend (e.g., `support@yourdomain.com`).

**Build Command:**
```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
```

**Start Command:**
```bash
gunicorn jangoproject.wsgi:application
```
