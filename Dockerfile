FROM ubuntu:18.04
COPY . ./app
WORKDIR /app
RUN apt-get -y upgrade && apt-get -y update && apt-get -y install python3 && apt-get -y install python3-pip
#RUN apt-get -y install build-essential libssl-dev libcurl4-gnutls-dev libexpat1-dev gettext unzip && apt-get -y install wget && apt-get -y install git

RUN pip3 install -r requirements.txt
CMD ["python3", "main.py"]
