FROM mvertes/alpine-mongo:latest
# Reference https://docs.docker.com/engine/reference/builder/#label
LABEL maintainer "mmaguero <marvin-aguero@hotmail.com>"

RUN apk update && apk upgrade && apk add mongodb-tools

COPY mongodb /etc/conf.d/

WORKDIR /root/

ENTRYPOINT [ "/root/run.sh" ]
CMD [ "mongod" ]
