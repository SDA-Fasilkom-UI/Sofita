FROM openjdk:8-alpine3.9

RUN apk update \
    && apk add --no-cache bash git make gcc libcap-dev musl-dev diffutils tzdata \
    python3 py3-pillow py3-lxml

RUN if [ ! -z "$HTTP_PROXY" ]; then git config --global http.proxy $HTTP_PROXY; fi

ENV ISOLATE_VERSION v1.8.1
RUN git clone --branch $ISOLATE_VERSION --depth 1 https://github.com/ioi/isolate \
    && cd isolate \
    && make install

RUN mkdir /graderng
WORKDIR /graderng

COPY requirements.txt /graderng/requirements.txt

RUN export HTTP_PROXY=$HTTP_PROXY
RUN export HTTPS_PROXY=$HTTP_PROXY
RUN echo $HTTP_PROXY $HTTPS_PROXY
RUN if [ ! -z "$HTTP_PROXY" ]; then pip3 --proxy $HTTP_PROXY --retries 1 install -r requirements.txt; \
    else pip3 install -r requirements.txt; fi

COPY . /graderng

ENTRYPOINT ["./entrypoint.sh"]
