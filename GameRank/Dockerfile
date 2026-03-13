# Usar una imagen base de Python
FROM python:3.12-slim
# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app
# Copiar los todos los ficheros del proyecto al contenedor
COPY . .
# comandos dentro del docker
RUN pip install -r requirements.txt \
    && python3 manage.py migrate \
    && python3 manage.py createsuperuser --noinput --username admin --email admin@example.com

# Puerto a exponer
EXPOSE 8000

# Lanzar la app al final (1 solo) (ó ENTRYPOINT ["python3", "manage.py", "runserver", "127.0.0.1:8000"])
CMD ["python3", "manage.py", "runserver", "localhost:8000"]
