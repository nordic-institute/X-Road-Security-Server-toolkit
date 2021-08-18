FROM python:3

WORKDIR /usr/src

RUN apt-get -qq update \
    && apt-get -qq upgrade \
    && apt-get -qq install \
    && apt-get -qq install git \
    && apt-get -qq install jq \
    && pip install virtualenv

RUN git clone --branch v3.0 https://github.com/nordic-institute/X-Road-Security-Server-toolkit.git toolkit \
    && cd toolkit \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --extra-index-url http://niis-xrdsst-development.s3-website-eu-west-1.amazonaws.com/ xrdsst --trusted-host niis-xrdsst-development.s3-website-eu-west-1.amazonaws.com \
    && make virtualenv

RUN mkdir -p ssh_keys \
    && ssh-keygen -f ./ssh_keys/id_rsa

CMD bash -l