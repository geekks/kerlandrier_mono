FROM python:3.12
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir -r /code/requirements.txt
COPY ./resources/python/ /code/resources/python/
COPY ./images /code
CMD ["python","-u", "filemonitoring.py", "sources"]