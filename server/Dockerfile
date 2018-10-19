FROM python:2.7.15-slim

LABEL maintainer="robertomlsoares@gmail.com"

COPY requirements.txt /screenshot-aas-server/

WORKDIR /screenshot-aas-server/

RUN pip install -r requirements.txt

COPY server/ /screenshot-aas-server/

CMD ["gunicorn", "-c", "config.py", "server:app"]
