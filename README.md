# 🎮 GameRank

GameRank is a full-stack web application built with Django for exploring, rating, and commenting on videogames. It aggregates data from multiple external sources (XML and public JSON APIs) and allows users to interact with games by posting reviews, voting on comments, and customizing their experience.

> 🌐 **Live demo:** [https://noelito.pythonanywhere.com/](https://noelito.pythonanywhere.com/)  
> 🕒 *Available until **August 2025***

---

## ✨ Features

- 🔐 **Authentication system** (login with protected resources):
  - **Global login password**: `xx34d23` (to access any resource different from the main -> `/`).
  - **User login or registration**: Use individual profiles getting registered and login in this app.
- 🎲 **Game catalog**: Games are loaded from an XML source and two public APIs (FreeToGame and MMOBomb), ordered by average score.
- 💬 **User interactions**: Comment, rate (0–5 stars), like/dislike comments.
- 🔎 **Game filters** by platform, genre, and publisher.
- 🧾 **Game detail pages** with user ratings, average score, and comment threads.
- 🧠 **Profile customization**: Font size and type, and username modifications.
- 📥 **Game import/export**: Automatically import data from external sources and export each game's data with a simple click.
- 🧪 **Test coverage**: Django's built-in test suite (unit and end-to-end).
- 🌍 **Internationalization**: Available in Spanish and English.
- 📱 **Responsive UI**: Bootstrap-based modern frontend.

---

## 🧩 Tech Stack

- **Backend**: Python 3.13, Django 5
- **Frontend**: HTML5, Bootstrap 4, HTMX
- **Database**: SQLite
- **DevOps & Deployment**: Docker, Kubernetes (K8s), Minikube, Nginx Ingress
- **Hosting**: PythonAnywhere (Cloud) & Localhost (Django runserver / K8s cluster)
- **External APIs**: FreeToGame, MMOBomb

---

## 🖥️ Deployment (Online)

The project is deployed and available at:

🔗 [https://noelito.pythonanywhere.com/](https://noelito.pythonanywhere.com/)  
🗓️ Valid until August 2025  
🔐 Default credentials (for demo purposes):

### 🔐 Users Credentials

- **Admin Panel**: `noelito / 123`  
- **Regular Users**: `gonza / gonzagonza14`, `lucia / lucialucia12`

---

## 📹 Demo Videos

- 🎥 [Basic Functionality](https://youtu.be/sqMIz6oc28I)
- 🎥 [Optional Features](https://youtu.be/3WCI0hEX_Mw)

---

## 🧑‍💻 Author

**Noel Rodríguez Pérez** Bachelor’s Degree in Telecommunications Engineering  
📫 [n.rodriguezp.2022@alumnos.urjc.es](mailto:n.rodriguezp.2022@alumnos.urjc.es) | [noelrp240514@gmail.com](mailto:noelrp240514@gmail.com)  
🌐 GitHub: [@nowelito28](https://github.com/nowelito28)

---

## 🚀 Quickstart (Local Setup - Traditional)

### 📦 Requirements

- Python 3.11+
- pip
- Virtual environment (recommended)

### 🔧 Installation (Linux/macOS)

```bash
# Clone the repository
git clone [https://github.com/nowelito28/Middleware-Java_based-.git](https://github.com/nowelito28/Middleware-Java_based-.git)
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

# Create a superuser to access the database -> /admin (optional)
python3 manage.py createsuperuser

# Run the development server
python3 manage.py runserver
```

## 🐳 Deployment (Docker & Kubernetes / Minikube)

You can also run GameRank locally in a containerized Kubernetes cluster using **Minikube** and the official Docker image.

### 📋 Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (or any container runtime)
- [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)

### 🔐 Users Credentials

- **Admin Panel**: `noelito / 123`  
- **Regular Users**: `gonza / gonzagonza14`, `lucia / lucialucia12`

### 🛠️ Cluster Setup & Execution

**1. Start Minikube and enable the Ingress addon:**

```bash
minikube start
minikube addons enable ingress
```

**2. Create a dedicated namespace and set it as default (optional):**

```bash
kubectl create namespace gamerank-ns
kubectl config set-context --current --namespace=gamerank-ns
```

**3. Deploy the application from Docker Hub:**

```bash
# We use the explicitly tagged version to ensure stability (latest)
kubectl create deployment gamerank-deploy --image=nowelito28/gamerank:1.0.4
```

**4. Expose the deployment (Create a Service):**

```bash
kubectl expose deployment gamerank-deploy --type=NodePort --port=8000
```

**5. Apply the Ingress configuration:**
Create a file named `gamerank-ingress.yaml` with the following content (using `nip.io` for automatic local DNS resolution):

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: gamerank-ingress
  namespace: gamerank-ns
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
    - host: gamerank.127.0.0.1.nip.io
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: gamerank-deploy
                port:
                  number: 8000
```

Apply it to the cluster:

```bash
kubectl apply -f gamerank-ingress.yaml
```

**6. Start the Minikube Tunnel (Required for macOS/Docker Desktop):**
Open a **new terminal tab** and run the following command. Leave it running in the background (it might ask for your admin password to bind to port 80):

```bash
minikube tunnel
```

**7. Access the application:** Open your web browser and navigate to:  
👉 **[http://gamerank.127.0.0.1.nip.io](http://gamerank.127.0.0.1.nip.io)**

*(Note: The Django `settings.py` is already configured to accept this `nip.io` host in the `ALLOWED_HOSTS` array in the `1.0.4` Docker image).*

**8. Create a Superuser in Kubernetes (Optional):**
If you need to create a new superuser directly inside the running Kubernetes cluster, you can execute Django commands inside the pod:

```bash
# First, find the exact name of your running pod
kubectl get pods -n gamerank-ns

# Then, execute the createsuperuser command inside that pod (replace <pod-name> by the actual pod running name)
kubectl exec -it <pod-name> -n gamerank-ns -- python manage.py createsuperuser
```

*(Note: Because SQLite is being used inside the container without a Persistent Volume, any changes made to the database, including new users, will be lost if the pod restarts).*

---
