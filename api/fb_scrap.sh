#!/bin/bash


# Obtenir le chemin absolu du script
SCRIPT_PATH=$(realpath "$0")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")
cd "$SCRIPT_DIR" || exit

# Activer l'environnement virtuel python
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
else
    echo "Erreur: pas de '.venv' trouvé. Veuillez créer l'environnement virtuel python"
    exit 1
fi

# Exécuter le script Python d'import des événements Facebook Kerlandrier
python manual_scripts.py import_ics
# Désactiver l'environnement virtuel python
deactivate