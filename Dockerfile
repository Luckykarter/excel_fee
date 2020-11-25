FROM python:3.8-slim
ENV PYTHONUNBUFFERED TRUE
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
COPY ./excelfee/pycel/ /code/excelfee/pycel/

RUN pip install pycel ./excelfee/pycel/
RUN pip install -r requirements.txt
COPY . /code/

RUN python manage.py makemigrations excelfee
RUN python manage.py migrate
#ENV PORT 8080
#EXPOSE 8080
CMD ["python", "manage.py", "runserver", "0.0.0.0:8003"]
#CMD exec gunicorn --bind 0.0.0.0:80 --workers 1 --threads 8 --timeout 0 django_server.wsgi:application