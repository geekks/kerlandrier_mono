# Kerlandrier - API

> Our own API to do miscellaneous stuff

## Set your environment variables

_Copy the `.env.example` file to `.env` and fill it with your own values._

**Warning**:there are **two** `.env` files, one  in the `api` folder and one in the `api/script` folder.

## Local dev

### Activate your Python [Virtual Environment](https://fastapi.tiangolo.com/virtual-environments/)

_Avoid messing up with your local Python installation._

**Do it once :**

```bash
python -m venv .venv # Create the venv
```
- For `UNIX`
```bash
source .venv/bin/activate # Active the venv in Linux bash
python -m pip install --upgrade pip # Upgrade pip, just in case
pip install -r requirements.txt # Install packages
```

- For `WINDOWS`
```bash
source .venv/Scripts/activate # Active the venv in Windonws bash
python -m pip install --upgrade pip # Upgrade pip, just in case
pip install -r requirements.txt # Install packages
```

### Run api
```bash
fastapi dev main.py --port 8001 # Should serve at http://127.0.0.1:8001 - Use 8001 in conjunction with Kerlandrier_front for current tests
```


## Launch with Docker

### `docker`
```bash
docker build -t kerlandrierapi . # build docker image
docker run -d --name kerlandrierapi -p 8001:8001 --env-file .env --env-file script/.env kerlandrierapi:latest
```

### `docker compose`
```bash
docker compose up --build --detach
```

> API should serve at http://localhost:8001 (http://127.0.0.1:8001 )

### FastAPI
- [RTFM](https://fastapi.tiangolo.com)
![alt text](image.png)