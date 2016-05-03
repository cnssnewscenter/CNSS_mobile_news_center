FROM pandada8/alpine-python:3
RUN sed -i "s/dl-cdn.alpinelinux.org/mirror.pandada8.me/" /etc/apk/repositories && apk add --update redis libxml2-dev libxslt-dev
ADD . /app
WORKDIR /app
RUN pip install --index-url=http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com  -r requirements.txt && pip install --index-url=http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com honcho
EXPOSE 8090
CMD honcho start
