#!/bin/bash

echo "🧪 Exécution des tests..."
./venv/bin/python -m pytest tests/ -v

if [ $? -eq 0 ]; then
    echo "✅ Tests réussis! Compilation en cours..."
    
    # Nettoyage des fichiers de build précédents
    rm -rf dist build *.spec
    
    # Compilation de l'application
    ./venv/bin/pyinstaller --name=Audio2Text \
                --windowed \
                --onefile \
                --add-data=src:src \
                --add-binary=/opt/homebrew/bin/ffmpeg:. \
                --hidden-import=speech_recognition \
                --hidden-import=pydub \
                --hidden-import=docx \
                --hidden-import=PyQt6 \
                src/main.py
    
    if [ $? -eq 0 ]; then
        echo "✅ Compilation réussie!"
        echo "📦 L'application se trouve dans le dossier dist/"
    else
        echo "❌ Erreur lors de la compilation"
        exit 1
    fi
else
    echo "❌ Les tests ont échoué. Correction nécessaire avant la compilation."
    exit 1
fi
