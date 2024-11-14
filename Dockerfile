FROM python:3.11.9-bookworm

WORKDIR /root/

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y libopencv-dev ffmpeg

COPY ./setup.py /root/MPDriver3/
RUN mkdir /root/MPDriver3/mpdriver \
    && pip install --no-cache-dir -e /root/MPDriver3

COPY ./mpdriver /root/MPDriver3/mpdriver
