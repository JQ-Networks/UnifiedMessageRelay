FROM python:3.6

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080
# Run as a foreground program
CMD [ "python", "daemon.py","run" ] 