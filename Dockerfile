FROM python:3.9-slim-buster
WORKDIR /usr/src/beebot
EXPOSE 8000
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . .
RUN chmod a+x run.sh
CMD ["./run.sh"]