FROM python:3.12
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir -r /code/requirements.txt
COPY ./libs/ /code/libs/
COPY ./mistral_images.py /code/mistral_images.py
CMD ["python","-u", "filemonitoring.py", "sources"]