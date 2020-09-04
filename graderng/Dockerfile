FROM ubuntu:20.04

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip git build-essential \
    libcap-dev openjdk-8-jdk

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
