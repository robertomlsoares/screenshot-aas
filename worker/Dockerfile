FROM python:2.7.15-slim

LABEL maintainer="robertomlsoares@gmail.com"

RUN apt-get update -y \
    && apt-get install -y wget unzip gnupg

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list

RUN apt-get update -y \
    && apt-get install -y curl google-chrome-stable

RUN mkdir /chromedriver/
RUN wget -q --continue -P /chromedriver/ "http://chromedriver.storage.googleapis.com/2.43/chromedriver_linux64.zip"
RUN unzip /chromedriver/chromedriver* -d /chromedriver/
ENV PATH /chromedriver:$PATH

COPY requirements.txt /screenshot-aas-worker/

WORKDIR /screenshot-aas-worker/

RUN pip install -r requirements.txt

COPY src /screenshot-aas-worker/

CMD ["python", "worker.py"]
