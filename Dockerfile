FROM python:3.6

WORKDIR /usr/src/app

# setup requirements.
RUN pip install --no-cache-dir pipenv &&\
    echo "deb http://www.deb-multimedia.org jessie main" >> /etc/apt/sources.list &&\
    wget http://www.deb-multimedia.org/pool/main/d/deb-multimedia-keyring/deb-multimedia-keyring_2016.8.1_all.deb &&\
    dpkg -i deb-multimedia-keyring_2016.8.1_all.deb &&\
    rm deb-multimedia-keyring_2016.8.1_all.deb &&\
    apt -y update && apt -y upgrade &&\
    apt -y install ffmpeg

COPY Pipfile* ./
RUN pipenv install -v

COPY . .

EXPOSE 8080

# Run as a foreground program
CMD ["pipenv", "run", "python", "daemon.py","run"] 
