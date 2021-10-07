FROM python:3.9-slim-buster
WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app

RUN pip install .

CMD ["uvicorn", "dummy_submitter:app", "--host", "0.0.0.0", "--port", "80", "--proxy-headers"]
