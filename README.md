# Audio2Text v1.0.0

Une application de bureau pour convertir des fichiers audio en texte avec une interface graphique conviviale.

## Fonctionnalités

- Conversion de fichiers audio en texte
- Support de multiples formats audio (.wav, .mp3, .m4a, .flac, .ogg)
- Interface graphique intuitive
- Traitement parallèle pour une conversion rapide
- Support multilingue (français par défaut)
- Export au format Word (.docx)

## Prérequis

- Python 3.13 ou supérieur
- FFmpeg installé sur le système

## Installation

```bash
# Cloner le dépôt
git clone https://github.com/yourusername/audio2text.git
cd audio2text

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Unix/macOS
# ou
venv\Scripts\activate  # Sur Windows

# Installer les dépendances
pip install -e .
```

## Utilisation

1. Lancer l'application :
```bash
audio2text
```

2. Cliquer sur "Sélectionner un fichier" pour choisir le fichier audio à convertir
3. Sélectionner la langue du fichier audio
4. Attendre la fin de la conversion
5. Le texte converti sera affiché et sauvegardé automatiquement au format Word

## Tests

Pour exécuter les tests :
```bash
python -m pytest tests/
```

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## Auteur

- Liv
