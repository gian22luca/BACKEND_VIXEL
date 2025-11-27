FROM python:3.12-alpine  

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 


WORKDIR /app

RUN apk add --no-cache \
    build-base \
    mariadb-dev \
    jpeg-dev \
    zlib-dev \
    openjpeg-dev \
    curl
    
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

COPY deployments/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

RUN mkdir -p /app/static_files /app/logs 

RUN adduser -D vixeluser

RUN chown -R vixeluser:vixeluser /app

RUN chmod -R 755 /app

USER vixeluser

EXPOSE 8000

ENTRYPOINT [ "/usr/local/bin/entrypoint.sh" ]

CMD ["production"]


