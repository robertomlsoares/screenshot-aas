FROM python:2.7.15-slim

LABEL maintainer="robertomlsoares@gmail.com"

EXPOSE 5000

COPY requirements.txt /screenshot-aas-worker/

WORKDIR /screenshot-aas-worker/

RUN pip install -r requirements.txt

COPY src /screenshot-aas-worker/

RUN apt-get update \
    && apt-get install -y curl iceweasel
RUN curl -L https://github.com/mozilla/geckodriver/releases/download/v0.23.0/geckodriver-v0.23.0-linux64.tar.gz | tar xz -C /usr/local/bin

CMD ["python", "worker.py"]
