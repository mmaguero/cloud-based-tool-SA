#
# To build:
# > sudo docker build -t scrapyrt .
#
# to start as daemon with port 9080 of api exposed as 9080 on host
# and host's directory ${PROJECT_DIR} mounted as /scrapyrt/project
#
# > sudo docker run -p 9080:9080 -tid -v ${PROJECT_DIR}:/scrapyrt/project scrapyrt
#

FROM frolvlad/alpine-python2
# Reference https://docs.docker.com/engine/reference/builder/#label
LABEL maintainer "mmaguero <marvin-aguero@hotmail.com>" 

RUN apk update && apk upgrade \
    && apk add python-dev git gcc linux-headers musl-dev wget libffi-dev libxml2-dev libxslt-dev zlib-dev openssl-dev

RUN mkdir -p /scrapyrt/src /scrapyrt/project
RUN mkdir -p /var/log/scrapyrt

RUN wget -O /tmp/get-pip.py "https://bootstrap.pypa.io/get-pip.py" --no-check-certificate && \
    python /tmp/get-pip.py "pip==9.0.1" && \
    rm /tmp/get-pip.py 

RUN pip install scrapyrt pymongo==3.4.0
RUN apk del git gcc linux-headers

WORKDIR /scrapyrt/project

COPY tripadvisorbot /scrapyrt/project/

ENTRYPOINT ["scrapyrt", "-i 0.0.0.0", "-s TIMEOUT_LIMIT=18000"]

EXPOSE 9080

