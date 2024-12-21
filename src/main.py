import sys
import os
import logging
from datetime import datetime
from pathlib import Path

# Ajouter le répertoire parent au chemin Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from src.main_window import MainWindow

def setup_logging():
    """Configure le système de logging"""
    try:
        # Créer le dossier logs s'il n'existe pas
        log_dir = Path(__file__).parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        # Configurer le fichier de log
        log_file = log_dir / 'audio2text.log'
        
        # Configuration du logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8', mode='w'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        # Définir le niveau de log pour les bibliothèques tierces
        logging.getLogger('pydub').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        
        logging.info("=== Démarrage de l'application Audio2Text ===")
        logging.info(f"Fichier de log : {log_file}")
        logging.info(f"Python version : {sys.version}")
        logging.info(f"Répertoire courant : {os.getcwd()}")
        logging.info(f"PYTHONPATH : {os.environ.get('PYTHONPATH', '')}")
        
    except Exception as e:
        print(f"Erreur lors de la configuration du logging : {e}")
        traceback.print_exc()
        sys.exit(1)

def excepthook(type_, value, traceback_):
    """Gestionnaire global des exceptions non gérées"""
    logging.critical("Exception non gérée:", exc_info=(type_, value, traceback_))
    try:
        if QApplication.instance():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setText("Une erreur critique s'est produite")
            msg.setInformativeText(str(value))
            msg.setDetailedText(''.join(traceback.format_tb(traceback_)))
            msg.setWindowTitle("Erreur Critique")
            msg.exec()
    except:
        pass
    sys.exit(1)

def main():
    """Point d'entrée principal de l'application"""
    try:
        # Installer le gestionnaire d'exceptions
        sys.excepthook = excepthook
        
        # Configurer le logging
        setup_logging()
        
        logging.debug("Création de l'application Qt")
        app = QApplication(sys.argv)
        
        logging.debug("Création de la fenêtre principale")
        window = MainWindow()
        
        logging.debug("Affichage de la fenêtre")
        window.show()
        
        logging.debug("Démarrage de la boucle d'événements")
        return app.exec()
        
    except Exception as e:
        logging.critical(f"Erreur fatale lors du démarrage de l'application : {e}", exc_info=True)
        try:
            if QApplication.instance():
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setText("Erreur fatale")
                msg.setInformativeText(str(e))
                msg.setWindowTitle("Erreur")
                msg.exec()
        except:
            pass
        return 1

if __name__ == '__main__':
    main()
