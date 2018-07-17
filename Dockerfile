FROM python:3.6-alpine

WORKDIR /usr/src/app

# setup requirements.
RUN pip install --no-cache-dir pipenv &&\
    apk update && apk upgrade &&\
    apk add ffmpeg

COPY Pipfile* ./
RUN pipenv install -v

COPY . .

EXPOSE 8080

# Run as a foreground program
CMD ["pipenv", "run", "python", "daemon.py","run"]