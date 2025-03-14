# Kerlandrier - APP

> Our own frontend

## Env setup

Copy `.env.example` to `.env` with your setup:
- VITE_API_URL:  Kerlandrier FastAPI URL you need access to [Kerlandrier API](https://github.com/geekks/Kerlandrier_api)
- VITE_OA_SLUG: Nom simplifié de l'agenda OA (https://openagenda.com/fr/VITE_OA_UID)
- VITE_OA_UID: UID de l'agenda OA
- VITE_OA_PUBLIC_KEY: OA Public Key

## Local dev (with Docker)

### `docker`
```bash
docker build -t kerlandrierfront . # build docker image
docker run -d --name kerlandrierfront -p 8090:5173 --env-file .env kerlandrierfront:latest
```

`docker compose`
```bash
docker compose up --build --detach
```

## Local dev (without Docker)

node version >= 20 

```bash
yarn # install dependencies
yarn dev # launch server on port 5173
```

_Hot reload by default_

> Available at http://localhost:8090