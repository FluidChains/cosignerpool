FROM golang:1.14
LABEL maintainer "Karim Boucher <karim.boucher@fluidchains.com>"


WORKDIR /go/src/app
COPY . .

RUN go build -o main .

ENTRYPOINT /go/src/app/main
