# Kerlandrier - APP

> Our own frontend

## Local dev

### Env setup

Copy `.env.example` to `.env` with your setup:
- VITE_API_URL:  Kerlandrier FastAPI URL you need access to [Kerlandrier API](https://github.com/geekks/Kerlandrier_api)
- VITE_OA_SLUG: Nom simplifié de l'agenda OA (https://openagenda.com/fr/VITE_OA_UID)
- VITE_OA_UID: UID de l'agenda OA
- VITE_OA_PUBLIC_KEY: OA Public Key


> Available at http://localhost:8090 (http://127.0.0.1:8090)

node version >= 22

```bash
yarn # install dependencies
yarn dev # launch server on port 5173
```



_Hot reload by default_

## Production


This application uses a `config.json` file to load runtime configuration, including your own keys that should not be into the JavaScript bundle, in docker image.

### Setup

1. Copy the example configuration:
```bash
cp config.json.example config.json
```

2. Edit `config.json` with your actual values:
```json
{
  "OA_PUBLIC_KEY": "your_actual_public_key_here",
  "API_URL": "https://api.kerlandrier.cc",
  "OA_SLUG": "kerlandrier",
  "OA_UID": "44891982"
}
```

3. Run:

- local build

```bash
docker compose build
docker compose up -d
```

- or pull docker image form github

```bash
docker compose pull
docker compose up -d
```
