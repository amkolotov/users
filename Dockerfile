FROM python:3.8

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTOCODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update -y && apt-get install netcat -y
RUN apt-get upgrade -y
RUN pip install --upgrade pip

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]