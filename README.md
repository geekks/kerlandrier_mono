# `app`

React app which serves the frontend

# `api`

Fastapi python api which serves the backend for various purposes:
- Authentication
- Keywords update

# `script`

Miscellaneous `shit` in `js` that turned into `python` and will be crammed into some `cron` `shit`

TO DO:

Faire un search des events & faire un meilleur match pour les noms des lieux

## Tests


Pour mesurer la couverture de l'API (dans `api/script`, seul `libs` est inclus)
et celle du code TypeScript du front :

```bash
python -m pytest --cov=api --cov-report=term-missing
cd app
corepack yarn install --immutable
corepack yarn test:coverage
```

Le rapport du front concerne les tests Vitest locaux ; les tests navigateur
pytest ci-dessous ne sont pas inclus dans ce rapport.
