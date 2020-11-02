FROM python:3.8.5
#ENV PYTHONUNBUFFERED 1
#RUN mkdir /config
RUN mkdir /src
WORKDIR /src

ADD requirements.txt /src
RUN pip install -r /src/requirements.txt

ADD . /src/

EXPOSE 8000
#CMD ["python", "manage.py", "runserver", "0.0.0.0", "8000"]
CMD ./run.sh
