# Dockerfile para backend
# FROM python:3.9
FROM python:3.10-slim AS tl-backend-flask_img
ENV PYTHONUNBUFFERED 1


ENV DEBIAN_FRONTEND noninteractive
ENV TZ=Europe/Madrid

RUN apt update && DEBIAN_FRONTEND=noninteractive apt install -y --no-install-recommends tzdata net-tools file wget tar sudo adduser nano htop netstat-nat net-tools curl less procps \
&& rm -rf /var/lib/apt/lists/* && pip install --upgrade pip

# # Create user ubuntu
# RUN useradd -m -s /bin/bash ubuntu && usermod -aG sudo ubuntu && echo "ubuntu ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/ubuntu \
# 	&& chmod 044 /etc/sudoers.d/ubuntu && echo 'ubuntu:ubuntu' | chpasswd

RUN useradd -m -s /bin/bash ubuntu && usermod -aG sudo ubuntu && echo "ubuntu ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/ubuntu \
&& chmod 044 /etc/sudoers.d/ubuntu && echo 'ubuntu:ubuntu' | chpasswd

ENV PATH="/home/ubuntu/.local/bin:$PATH"

USER ubuntu:ubuntu

WORKDIR /home/ubuntu/
COPY --chown=ubuntu:ubuntu requirements.txt /home/ubuntu/
RUN pip install -r requirements.txt --upgrade pip

WORKDIR /home/ubuntu/app/tl-backend-flask

# RUN sudo chown ubuntu:ubuntu /home/ubuntu/app/backend-drf && sudo chmod 777 -R /home/ubuntu/app/backend-drf

CMD python main.py
# CMD bash