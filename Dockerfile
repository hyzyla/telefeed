FROM python:3.7.2

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /work/requirements.txt

WORKDIR /work

RUN pip install -r requirements.txt

COPY . /work

