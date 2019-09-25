FROM python:3.7

COPY . /app

WORKDIR /app/src

RUN pip install --user plyvel 

EXPOSE ${COSIGNER_SERVICE_PORT}

ENTRYPOINT exec python3 cosignerpool.py

