#!/bin/bash

set -e

cd graderng
docker-compose build
docker-compose up -d
