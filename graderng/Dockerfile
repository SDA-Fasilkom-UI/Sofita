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

RUN if [ ! -z "$HTTP_PROXY" ]; then pip3 --proxy $HTTP_PROXY install --no-build-isolation -r requirements.txt; \
    else pip3 install -r requirements.txt; fi

COPY . /graderng

ENTRYPOINT ["./entrypoint.sh"]
