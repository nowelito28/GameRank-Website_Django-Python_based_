# 🎮 GameRank

GameRank is a full-stack web application built with Django for exploring, rating, and commenting on videogames. It aggregates data from multiple external sources (XML and public JSON APIs) and allows users to interact with games by posting reviews, voting on comments, and customizing their experience.

> 🌐 Live demo: [https://noelito.pythonanywhere.com/](https://noelito.pythonanywhere.com/)  
> 🕒 Available until **August 2025**

---

## ✨ Features

- 🔐 **Authentication system** (login with protected resources):
- - **Global login password**: xx34d23 (to access any resource different from the main -> '/').
- - **User login or registration**: Use individual profiles getting registered and login in this app.
- 🎲 **Game catalog**: games are loaded from an XML source and two public APIs (FreeToGame and MMOBomb), ordered by score average.
- 💬 **User interactions**: comment, rate (0–5 stars), like/dislike comments.
- 🔎 **Game filters** by platform, genre and publisher.
- 🧾 **Game detail pages** with user ratings, average score, and comment threads.
- 🧠 **Profile customization**: font size and type, and also the username.
- 📥 **Game import/export**: it is import data from external sources automatically and you can export also each data game with a simple click.
- 🧪 **Test coverage**: with Django's built-in test suite (unit and end-to-end).
- 🌍 **Internationalization**: available in Spanish and English.
- 📱 **Responsive UI**: Bootstrap-based modern frontend.

---

## 🧩 Tech Stack

- **Backend**: Python 3.13, Django 5
- **Frontend**: HTML5, Bootstrap 4, HTMX
- **Database**: SQLite
- **Launch**: PythonAnywhere and even in localhost by Django's runserver
- **Testing**: Django Test Framework
- **External APIs**: FreeToGame, MMOBomb

---

## 🖥️ Deployment (Online)

The project is deployed and available at:

🔗 [https://noelito.pythonanywhere.com/](https://noelito.pythonanywhere.com/)  
🗓️ Valid until August 2025  
🔐 Default credentials (for demo purposes):  
- **Admin Panel**: `noelito / 123`  
- **Regular Users**: `lucia / lucialucia12`, `gonza / gonzagonza14`

---

## 📹 Demo Videos

- 🎥 [Basic Functionality](https://youtu.be/sqMIz6oc28I)
- 🎥 [Optional Features](https://youtu.be/3WCI0hEX_Mw)

---

## 🧑‍💻 Author

**Noel Rodríguez Pérez**  
Bachelor’s Degree in Telecommunications Engineering  
📫 n.rodriguezp.2022@alumnos.urjc.es <--> noelrp240514@gmail.com
🌐 GitHub: [@nowelito28](https://github.com/nowelito28)

---

## 🚀 Quickstart (Local Setup)

### 📦 Requirements

- Python 3.11+
- pip
- Virtual environment (recommended)

### 🔧 Installation (Linux/MacOs)

```bash
# Clone the repository
git clone https://github.com/nowelito28/Middleware-Java_based-.git
cd Middleware-Java_based-  # or the real repo name

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install project dependencies
pip install -r GameRank/requirements.txt

# Navigate to Django project folder
cd GameRank

# Apply migrations
python3 manage.py migrate

# Create a superuser to access the data base -> /admin (optional)
python3 manage.py createsuperuser

# Run the development server
python3 manage.py runserver
