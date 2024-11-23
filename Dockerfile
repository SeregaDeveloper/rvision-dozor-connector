FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN pip install requests && \
    pip install --no-cache -r requirements.txt

ENTRYPOINT [ "python3", "./dozor-to-rvision.py" ]
