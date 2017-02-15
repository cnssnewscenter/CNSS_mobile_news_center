FROM pandada8/alpine-python:3
RUN sed -i "s/dl-6.alpinelinux.org/mirror.pandada8.me/" /etc/apk/repositories && apk add --update redis libxml2-dev libxslt-dev
RUN sed -i "s/daemonize yes/daemonize no/" /etc/redis.conf
ADD requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir --index-url=http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com  -r requirements.txt
ADD . /app
EXPOSE 8090
CMD python /app/app.py
