FROM python:3.13-slim
WORKDIR /api
COPY ./requirements.txt /api/requirements.txt
RUN pip install --no-cache-dir -r /api/requirements.txt
COPY . /api
EXPOSE 8001
CMD ["uvicorn", "main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8001"]
