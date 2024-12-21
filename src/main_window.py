import os
import sys
import logging
from pathlib import Path

# Ajouter le répertoire parent au chemin Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog,
                            QTextEdit, QScrollArea, QComboBox, QMessageBox, QLabel, QProgressBar, QHBoxLayout)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QTextCursor
from src.audio_converter import AudioConverter

class ConversionThread(QThread):
    progress_updated = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, audio_path, language):
        super().__init__()
        self.audio_path = audio_path
        self.language = language
        self.is_running = False
    
    def run(self):
        try:
            self.is_running = True
            converter = AudioConverter()
            
            # Lancer la conversion
            result = converter.convert_to_text(self.audio_path, self.language)
            if result:
                self.finished.emit(result)
            
        except Exception as e:
            error_msg = f"Erreur lors de la conversion : {str(e)}"
            logging.error(error_msg, exc_info=True)
            self.error.emit(error_msg)
        finally:
            self.is_running = False
    
    def stop(self):
        self.is_running = False

class LogHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        self.text_widget.document().setMaximumBlockCount(1000)  # Limiter le nombre de lignes
        
        # Format personnalisé pour les logs
        self.formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # Couleurs pour les différents niveaux de log
        self.colors = {
            logging.DEBUG: '#808080',    # Gris
            logging.INFO: '#FFFFFF',     # Blanc
            logging.WARNING: '#FFA500',  # Orange
            logging.ERROR: '#FF0000',    # Rouge
            logging.CRITICAL: '#FF0000'  # Rouge
        }
    
    def emit(self, record):
        try:
            # Formater le message
            msg = self.formatter.format(record)
            color = self.colors.get(record.levelno, '#FFFFFF')
            
            # Créer le HTML avec la couleur appropriée
            html = f'<span style="color: {color};">{msg}</span><br>'
            
            # Ajouter le message au widget
            self.text_widget.append(html)
            
            # Faire défiler jusqu'au bas
            scrollbar = self.text_widget.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
            
        except Exception as e:
            print(f"Erreur dans LogHandler.emit: {e}")

class MainWindow(QMainWindow):
    # Dictionnaire des langues supportées
    SUPPORTED_LANGUAGES = {
        'Français': 'fr-FR',
        'English (US)': 'en-US',
        'English (UK)': 'en-GB',
        'Deutsch': 'de-DE',
        'Español': 'es-ES',
        'Italiano': 'it-IT',
        'Nederlands': 'nl-NL',
        'Polski': 'pl-PL',
        'Português': 'pt-PT',
        'Русский': 'ru-RU',
        '日本語': 'ja-JP',
        '한국어': 'ko-KR',
        '中文': 'zh-CN'
    }
    
    def __init__(self):
        try:
            logging.info("Initialisation de MainWindow")
            super().__init__()
            self.setWindowTitle("Audio2Text Converter")
            self.setMinimumSize(800, 600)
            
            # Initialiser les variables
            self.conversion_thread = None
            self.converter = AudioConverter()
            
            logging.info("Création des widgets")
            self._create_widgets()
            
        except Exception as e:
            logging.error(f"Erreur dans l'initialisation de MainWindow: {str(e)}", exc_info=True)
            self.show_error_dialog("Erreur d'initialisation", str(e))
            raise
    
    def show_error_dialog(self, title, message):
        """Affiche une boîte de dialogue d'erreur"""
        try:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setText(title)
            msg.setInformativeText(message)
            msg.setWindowTitle("Erreur")
            msg.exec()
        except Exception as e:
            logging.error(f"Erreur lors de l'affichage de la boîte de dialogue : {str(e)}")
    
    def _create_widgets(self):
        try:
            # Widget et layout principal
            main_widget = QWidget()
            self.setCentralWidget(main_widget)
            layout = QVBoxLayout(main_widget)
            
            # Labels d'information
            self.title_label = QLabel("Audio2Text Converter")
            self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
            self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            self.info_label = QLabel("Sélectionnez un fichier audio à convertir")
            self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Layout horizontal pour le sélecteur de langue et le bouton
            select_layout = QHBoxLayout()
            
            # Sélecteur de langue
            self.language_combo = QComboBox()
            self.language_combo.addItems(self.SUPPORTED_LANGUAGES.keys())
            # Sélectionner Français par défaut
            self.language_combo.setCurrentText('Français')
            self.language_combo.setStyleSheet("""
                QComboBox {
                    padding: 5px;
                    font-size: 14px;
                    border: 1px solid #ccc;
                    border-radius: 3px;
                    min-width: 150px;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox::down-arrow {
                    image: url(down_arrow.png);
                    width: 12px;
                    height: 12px;
                }
            """)
            
            # Bouton de sélection de fichier
            self.select_button = QPushButton("Sélectionner un fichier audio")
            self.select_button.setStyleSheet("""
                QPushButton {
                    padding: 10px;
                    font-size: 16px;
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QPushButton:disabled {
                    background-color: #cccccc;
                }
            """)
            self.select_button.clicked.connect(self.select_file)
            
            # Ajouter les widgets au layout horizontal
            select_layout.addWidget(self.language_combo)
            select_layout.addWidget(self.select_button)
            
            # Barre de progression
            self.progress = QProgressBar()
            self.progress.setVisible(False)
            self.progress.setStyleSheet("""
                QProgressBar {
                    border: 2px solid grey;
                    border-radius: 5px;
                    text-align: center;
                    height: 25px;
                    margin: 10px 0;
                }
                QProgressBar::chunk {
                    background-color: #4CAF50;
                    width: 20px;
                }
            """)
            
            # Zone de logs avec titre
            log_title = QLabel("Logs de l'application")
            log_title.setStyleSheet("""
                font-size: 16px;
                font-weight: bold;
                margin: 10px 0;
                color: #ffffff;
            """)
            
            # Zone de logs
            self.log_viewer = QTextEdit()
            self.log_viewer.setReadOnly(True)
            self.log_viewer.setMinimumHeight(300)
            self.log_viewer.setStyleSheet("""
                QTextEdit {
                    background-color: #1e1e1e;
                    color: #ffffff;
                    font-family: 'Courier New';
                    font-size: 12px;
                    padding: 10px;
                    border: 1px solid #333;
                    border-radius: 5px;
                }
            """)
            
            # Configuration du handler de logs
            log_handler = LogHandler(self.log_viewer)
            logging.getLogger().addHandler(log_handler)
            logging.getLogger().setLevel(logging.DEBUG)
            
            # Ajouter les widgets au layout principal
            layout.addWidget(self.title_label)
            layout.addWidget(self.info_label)
            layout.addLayout(select_layout)
            layout.addWidget(self.progress)
            layout.addWidget(log_title)
            layout.addWidget(self.log_viewer, 1)
            
            logging.info("Interface graphique initialisée")
            
        except Exception as e:
            logging.error(f"Erreur dans la création des widgets: {str(e)}", exc_info=True)
            self.show_error_dialog("Erreur de création des widgets", str(e))
            raise

    def update_progress(self, current):
        """Met à jour la barre de progression"""
        try:
            self.progress.setValue(current)
            logging.debug(f"Progression mise à jour: {current}")
        except Exception as e:
            logging.error(f"Erreur lors de la mise à jour de la progression: {str(e)}")
            self.show_error_dialog("Erreur de progression", str(e))

    def log_progress(self, message):
        """Ajoute un message dans la zone de logs"""
        try:
            logging.info(message)
        except Exception as e:
            logging.error(f"Erreur lors de l'ajout du message de log: {str(e)}")

    def handle_error(self, error_message):
        """Gère les erreurs de conversion"""
        logging.error(error_message)
        self.info_label.setText("Erreur lors de la conversion")
        self.select_button.setEnabled(True)
        self.language_combo.setEnabled(True)
        self.progress.setVisible(False)
        
        # Afficher l'erreur dans une boîte de dialogue
        self.show_error_dialog("Erreur de conversion", error_message)

    def select_file(self):
        """Gère la sélection du fichier audio et lance la conversion"""
        try:
            logging.info("Ouverture du sélecteur de fichier")
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Sélectionner un fichier audio",
                "",
                "Fichiers audio (*.mp3 *.wav *.m4a *.ogg *.flac)"
            )
            
            if file_path:
                logging.info(f"Fichier sélectionné : {file_path}")
                self.progress.setVisible(True)
                self.progress.setValue(0)
                self.info_label.setText("Conversion en cours...")
                self.select_button.setEnabled(False)
                self.language_combo.setEnabled(False)
                
                # Récupérer le code de langue sélectionné
                selected_language = self.SUPPORTED_LANGUAGES[self.language_combo.currentText()]
                logging.info(f"Langue sélectionnée: {selected_language}")
                
                # Arrêter le thread précédent s'il existe
                if self.conversion_thread and self.conversion_thread.is_running:
                    logging.warning("Arrêt du thread de conversion précédent")
                    self.conversion_thread.stop()
                    self.conversion_thread.wait()
                
                # Créer et démarrer le thread de conversion
                self.conversion_thread = ConversionThread(file_path, selected_language)
                self.conversion_thread.progress_updated.connect(self.update_progress)
                self.conversion_thread.finished.connect(self.on_conversion_finished)
                self.conversion_thread.error.connect(self.handle_error)
                self.conversion_thread.start()
                
        except Exception as e:
            error_msg = f"Erreur dans la sélection du fichier: {str(e)}"
            logging.error(error_msg, exc_info=True)
            self.show_error_dialog("Erreur de sélection", error_msg)
            self.handle_error(error_msg)

    def on_conversion_finished(self, result):
        """Appelé quand la conversion est terminée"""
        try:
            self.select_button.setEnabled(True)
            self.language_combo.setEnabled(True)
            self.info_label.setText("Conversion terminée !")
            self.progress.setVisible(False)
            logging.info("Conversion terminée avec succès")
            logging.info(f"Résultat : {result[:100]}...")  # Afficher les 100 premiers caractères
        except Exception as e:
            logging.error(f"Erreur lors de la finalisation de la conversion: {str(e)}")
            self.show_error_dialog("Erreur de finalisation", str(e))

    def stop_conversion(self):
        """Arrête la conversion en cours"""
        if self.conversion_thread and self.conversion_thread.is_running:
            logging.info("Arrêt de la conversion en cours...")
            self.conversion_thread.stop()
            self.conversion_thread.wait()
            logging.info("Conversion arrêtée")
            self.progress.setValue(0)
            self.select_button.setEnabled(True)
            self.language_combo.setEnabled(True)
            self.log_viewer.append("Conversion arrêtée par l'utilisateur")

    def closeEvent(self, event):
        """Gérer la fermeture propre de l'application"""
        try:
            if self.conversion_thread and self.conversion_thread.is_running:
                logging.info("Arrêt du thread de conversion avant la fermeture")
                self.conversion_thread.stop()
                self.conversion_thread.wait()
            event.accept()
        except Exception as e:
            logging.error(f"Erreur lors de la fermeture de l'application: {str(e)}", exc_info=True)
            self.show_error_dialog("Erreur de fermeture", str(e))
            event.accept()
