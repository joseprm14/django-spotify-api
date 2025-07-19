FROM python:3.10-alpine

RUN pip install --upgrade pip

WORKDIR /app
COPY . .

# Instalando dependencias
RUN pip install -r requirements.txt

# Exponer el puerto en el que corre Django (por defecto 8000)
EXPOSE 8000

CMD ["gunicorn", "spotify_project.wsgi:application", "--bind", "0.0.0.0:8000"]
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]