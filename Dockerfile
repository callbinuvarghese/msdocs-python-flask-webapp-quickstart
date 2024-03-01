# syntax=docker/dockerfile:1

FROM python:3.11

 # Supplied from container. Default value below
ARG APP_INSIGHTS_KEY="00000000-1111-1111-1111-000000000000"
    
WORKDIR /code

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 50505

ENTRYPOINT ["gunicorn", "app:app"]
