FROM python:3.8
MAINTAINER Wang Zhiwei <wangzhiwei@patsnap.com>


RUN apt-get update -y > /dev/null 2>&1 && \
    apt-get install -y python3-pip > /dev/null 2>&1 && \
    pip3 install pip -i "https://pypi.tuna.tsinghua.edu.cn/simple" > /dev/null 2>&1 --upgrade

WORKDIR /sqlgen

COPY sqlgen/ ./sqlgen
COPY requirements.txt setup.py setup.cfg __main__.py README.md ./

RUN pip3 install --no-cache-dir -i "https://pypi.tuna.tsinghua.edu.cn/simple" -r requirements.txt > /dev/null 2>&1

RUN apt-get -y clean all && \
    rm -rf /var/cache

RUN python3 setup.py install

EXPOSE 8080

ENTRYPOINT ["python3", "sqlgen/web.py"]
