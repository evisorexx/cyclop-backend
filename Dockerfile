FROM jjanzic/docker-python3-opencv

RUN pip install --upgrade pip


COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./cy_backend /app

WORKDIR /app

COPY ./entrypoint.sh /
ENTRYPOINT ["sh", "/entrypoint.sh"]

