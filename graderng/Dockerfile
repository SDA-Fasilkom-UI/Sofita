FROM openjdk:8-alpine3.9

RUN apk update \
    && apk add --no-cache bash git make gcc libcap-dev musl-dev diffutils \
    python3 py3-pillow

ENV ISOLATE_VERSION v1.8.1
RUN git clone --branch $ISOLATE_VERSION --depth 1 https://github.com/ioi/isolate \
    && cd isolate \
    && make install

RUN mkdir /graderng
COPY . /graderng
WORKDIR /graderng

RUN pip3 install -r requirements.txt

ENTRYPOINT ["./entrypoint.sh"]
