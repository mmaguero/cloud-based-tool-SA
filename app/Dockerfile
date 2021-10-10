FROM frolvlad/alpine-python3
# Reference https://docs.docker.com/engine/reference/builder/#label
LABEL maintainer "mmaguero <marvin-aguero@hotmail.com>"

RUN apk update && apk upgrade \
    && apk add git supervisor gcc linux-headers python3-dev musl-dev freetype-dev libjpeg-turbo-dev lcms2-dev openjpeg-dev tiff-dev libwebp-dev libxml2-dev libxslt-dev zlib-dev \
    && pip install uwsgi 

COPY djproject /home/Gastro-miner/

COPY requirements.txt /home/Gastro-miner/

RUN echo "http://dl-2.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories; \
    echo "http://dl-3.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories; \
    echo "http://dl-4.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories; \
    echo "http://dl-5.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories

RUN apk add --no-cache ca-certificates
 
RUN pip3 --no-cache-dir install --upgrade pip setuptools

RUN apk add --no-cache tini libstdc++ gcc freetype zlib jpeg libpng graphviz && \
    apk add --no-cache \
        --repository=http://dl-cdn.alpinelinux.org/alpine/edge/community \
        lapack-dev && \
    apk add --no-cache \
        --virtual=.build-dependencies \
        g++ gfortran musl-dev pkgconfig freetype-dev jpeg-dev zlib-dev libpng-dev make \
        python3-dev libc-dev && \
    ln -s locale.h /usr/include/xlocale.h

RUN pip3 install -r /home/Gastro-miner/requirements.txt 

RUN apk del git gcc linux-headers

RUN rm /usr/include/xlocale.h && \
    rm -rf /root/.cache && \
    rm -rf /var/cache/apk/* && \
    apk del .build-dependencies 

EXPOSE 8000

COPY app.ini /home/Gastro-miner/uwsgi/
COPY supervisord.conf /etc/

COPY nltk_data /root/nltk_data/

CMD ["supervisord", "-n"]
