FROM python:3.6-alpine

WORKDIR /usr/src/app

# setup requirements.
RUN pip install --no-cache-dir pipenv &&\
    apk update && apk upgrade &&\
    apk add libressl-dev build-base python-dev py-pip jpeg-dev zlib-dev curl-dev ffmpeg libwebp libwebp-dev

COPY Pipfile* ./
RUN pipenv install -v

COPY . .

EXPOSE 8080

# Run as a foreground program
CMD ["pipenv", "run", "python", "daemon.py","run"]
