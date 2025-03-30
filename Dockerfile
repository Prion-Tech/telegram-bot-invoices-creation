FROM python:3.12-slim

# dependencis for MacOS
#RUN apt-get update
#RUN apt-get install -y gcc python3-dev
#RUN apt-get clean
#RUN rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip uv

WORKDIR /code
COPY ./app/requirements.txt /code/requirements.txt

RUN uv pip install --system --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

CMD ["python", "-m", "app.main"]