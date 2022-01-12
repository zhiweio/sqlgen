FROM python:3.8-alpine
MAINTAINER Wang Zhiwei <wangzhiwei@patsnap.com>


WORKDIR /sqlgen

COPY sqlgen/ ./sqlgen
COPY requirements.txt setup.py setup.cfg __main__.py README.md ./

RUN pip3 install --no-cache-dir -i "https://pypi.tuna.tsinghua.edu.cn/simple" -r requirements.txt > /dev/null 2>&1

RUN python3 setup.py install

EXPOSE 8080

ENTRYPOINT ["python3", "sqlgen/web.py"]
