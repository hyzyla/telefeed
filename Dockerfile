FROM python:3.7.2

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements/dev.txt /work/requirements/dev.txt

WORKDIR /work

RUN pip install -r /work/requirements/dev.txt

COPY . /work

