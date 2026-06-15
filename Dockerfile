
FROM docker.io/library/python:3.11-slim


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


WORKDIR /app


COPY requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt


COPY . .


EXPOSE 8000


WORKDIR /app/production_report


CMD ["gunicorn", "--bind", "0.0.0.0:8000", "production_report.wsgi:application"]
