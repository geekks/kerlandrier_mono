FROM python:3.12-slim
WORKDIR /api
COPY ./requirements.txt /api/requirements.txt
RUN pip install --no-cache-dir -r /api/requirements.txt
COPY . /api
EXPOSE 8001
CMD ["fastapi", "run", "main.py","--proxy-headers", "--port", "8001"]
