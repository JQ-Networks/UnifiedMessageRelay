FROM python:3.6

WORKDIR /usr/src/app

RUN pip install --no-cache-dir pipenv
COPY Pipfile* ./
RUN pipenv install

COPY . .

EXPOSE 8080
# Run as a foreground program
CMD ["pipenv", "run", "python", "daemon.py","run"] 