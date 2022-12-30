FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN apt update -y
RUN apt install wakeonlan

COPY . .

CMD ["sh", "start.sh"]
