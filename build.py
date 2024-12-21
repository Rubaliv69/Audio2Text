import PyInstaller.__main__
import sys
import os

def build():
    # Déterminer le système d'exploitation
    is_windows = sys.platform.startswith('win')
    
    # Options de base pour PyInstaller
    options = [
        'src/main.py',  # Script principal
        '--name=Audio2Text',  # Nom de l'exécutable
        '--onefile',  # Créer un seul fichier
        '--noconsole',  # Pas de console en arrière-plan
        '--clean',  # Nettoyer avant la compilation
        '--add-data=LICENSE:.' if is_windows else '--add-data=LICENSE:.',
    ]
    
    # Lancer la compilation
    PyInstaller.__main__.run(options)

if __name__ == '__main__':
    build()
