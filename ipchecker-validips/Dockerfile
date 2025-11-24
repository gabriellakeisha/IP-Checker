# use official Python base image
FROM --platform=linux/amd64 python:3.9-slim

# set workign dir
WORKDIR /app

# copy requirements
COPY requirements.txt .

# install requirements
RUN pip install --no-cache-dir -r requirements.txt

# copy app
COPY src/app.py .

# expose port
EXPOSE 80

# set environment variable
ENV FLASK_APP=app.py

# run app
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=80"]
