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

Depuis la racine du dépôt :

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r api/requirements.txt -r requirements-test.txt
python -m pytest
```

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

Pour les tests d'intégration, copier `tests/.env.example` vers `tests/.env` et
le compléter. Pytest charge ce fichier automatiquement ; les variables déjà
présentes dans l'environnement ont priorité.

Par défaut, seuls les tests locaux sont exécutés. Les tests suivants nécessitent
une activation explicite :

```bash
# Front déjà démarré : affichage des événements et connexion.
python -m playwright install chromium
python -m pytest -m front --live-front -v

# Extraction réelle de l'affiche par Mistral (appel potentiellement payant).
python -m pytest -m mistral --live-mistral -v

# Correspondance du lieu extrait avec l'agenda de test, sans publication.
python -m pytest -m "mistral and openagenda" --live-mistral --live-openagenda -v

# Création puis suppression sur l'agenda de test uniquement.
python -m pytest -m openagenda --live-openagenda -v
```

Pour OpenAgenda, renseigner dans `tests/.env` l'UID d'un lieu de l'agenda de
test, une clé publique pour le lire et une clé secrète autorisée à y écrire.
Le test de correspondance ne crée pas de lieu si aucun lieu existant ne correspond.
