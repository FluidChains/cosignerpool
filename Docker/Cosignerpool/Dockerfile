FROM python:3.7

COPY . /app

WORKDIR /app

RUN pip install --user -r requirements.txt

WORKDIR /app/src

EXPOSE ${COSIGNER_SERVICE_PORT}

ENTRYPOINT exec python3 cosignerpool.py

