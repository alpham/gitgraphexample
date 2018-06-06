FROM python:3.6

COPY . /app

WORKDIR /app

CMD python3 -m gitgraph_server
