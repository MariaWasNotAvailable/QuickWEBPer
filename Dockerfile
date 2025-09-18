FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/webper

COPY requirements.txt ./
RUN python3 -m venv .venv
RUN source .venv/bin/activate
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python3", "-u", "webper.py" ]