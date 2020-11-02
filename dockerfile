FROM python:3.8-slim-buster
#ENV PYTHONUNBUFFERED 1
#RUN mkdir /config
RUN mkdir /src
WORKDIR /src

ADD requirements.txt /src
RUN pip3 install -r /src/requirements.txt

ADD . /src/

EXPOSE 8000
#CMD ["python", "manage.py", "runserver", "0.0.0.0", "8000"]
CMD ./run.sh
