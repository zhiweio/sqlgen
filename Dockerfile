FROM python:3.8
MAINTAINER Wang Zhiwei <wangzhiwei@patsnap.com>


RUN apt-get update -y && \
    apt-get install -y python3-pip && \
    pip3 install pip --upgrade

WORKDIR /sqlgen

COPY sqlgen/ ./sqlgen
COPY requirements.txt setup.py setup.cfg __main__.py ./

RUN pip3 install --no-cache-dir -r requirements.txt

RUN apt-get -y clean all && \
    rm -rf /var/cache

EXPOSE 8080

ENTRYPOINT ["python", "sqlgen/web.py"]
