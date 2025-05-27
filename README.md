# 🎮 GameRank

GameRank is a full-stack web application built with Django for exploring, rating, and commenting on videogames. It aggregates data from multiple external sources (XML and public JSON APIs) and allows users to interact with games by posting reviews, voting on comments, and customizing their experience.

> 🌐 Live demo: [https://noelito.pythonanywhere.com/](https://noelito.pythonanywhere.com/)  
> 🕒 Available until **August 2025**

---

## ✨ Features

- 🔐 **Authentication system** (login with protected resources).
- 🎲 **Game catalog**: games are loaded from an XML source and two public APIs (FreeToGame and MMOBomb).
- 💬 **User interactions**: comment, rate (0–5 stars), like/dislike comments.
- 🔎 **Game filters** by platform and genre.
- 🧾 **Game detail pages** with user ratings, average score, and comment threads.
- 🧠 **Profile customization**: font size, type, and user configuration.
- 📥 **Game import**: superusers can import data from external sources via a single click.
- 📄 **JSON endpoint**: for each game at `/juego/<id>.json`.
- 🧪 **Test coverage**: with Django's built-in test suite (unit and end-to-end).
- 🌍 **Internationalization**: available in Spanish and English.
- 📱 **Responsive UI**: Bootstrap-based modern frontend.

---

## 🧩 Tech Stack

- **Backend**: Python 3.13, Django 5
- **Frontend**: HTML5, Bootstrap 4, HTMX
- **Database**: SQLite
- **Deployment**: PythonAnywhere
- **Testing**: Django Test Framework
- **External APIs**: FreeToGame, MMOBomb

---

## 🖥️ Deployment (Online)

The project is deployed and available at:

🔗 [https://noelito.pythonanywhere.com/](https://noelito.pythonanywhere.com/)  
🗓️ Valid until August 2025  
🔐 Default credentials (for demo purposes):  
- **Admin Panel**: `noelito / 123`  
- **Regular Users**: `lucia / lucialucia12`, `gonza / gonza14`

---

## 📹 Demo Videos

- 🎥 [Basic Functionality](https://youtu.be/sqMIz6oc28I)
- 🎥 [Optional Features](https://youtu.be/3WCI0hEX_Mw)

---

## 🧑‍💻 Author

**Noel Rodríguez Pérez**  
Bachelor’s Degree in Telecommunications Engineering  
📫 n.rodriguezp.2022@alumnos.urjc.es  
🌐 GitHub: [@nowelito28](https://github.com/nowelito28)

---

## 📄 License

This project is licensed for educational and demonstration purposes.

---

## 🚀 Quickstart (Local Setup)

### 📦 Requirements

- Python 3.11+
- pip
- Virtual environment (recommended)

### 🔧 Installation

```bash
# Clone the repository
git clone https://github.com/nowelito28/Middleware-Java_based-.git
cd Middleware-Java_based-  # or the real repo name

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r GameRank/requirements.txt

# Navigate to Django project folder
cd GameRank

# Apply migrations
python3 manage.py migrate

# Create a superuser to access the data base -> /admin (optional)
python3 manage.py createsuperuser

# Run the development server
python manage.py runserver
