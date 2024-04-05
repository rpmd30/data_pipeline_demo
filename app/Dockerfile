FROM python:3.11

LABEL MAINTAINER="Ravi Patel rpmd30@gmail.com"

WORKDIR /var/app/

ADD ./requirements.txt /var/app/requirements.txt
RUN pip3 install -r requirements.txt
ADD . /var/app/

CMD [ "python3","main.py"]