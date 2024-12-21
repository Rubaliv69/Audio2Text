import os
import logging
import subprocess
import tempfile
import wave
from pathlib import Path
from pydub import AudioSegment
import speech_recognition as sr
from docx import Document
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from typing import List, Tuple
from PyQt6.QtCore import QObject, pyqtSignal, Qt
import datetime
import gc

class AudioConverter(QObject):
    # Signaux pour la progression
    progress_updated = pyqtSignal(int, int)  # (segments_traités, total_segments)
    segment_completed = pyqtSignal(str)  # message de log pour chaque segment
    error_occurred = pyqtSignal(str)  # Signal pour les erreurs
    
    def __init__(self, max_workers=None):
        super().__init__()
        # Utiliser le nombre de threads CPU disponibles - 1 (minimum 1)
        self.max_workers = max_workers or max(1, os.cpu_count() - 1)
        self.language = 'fr-FR'  # Langue par défaut
        logging.info(f"Initialisation du convertisseur audio avec {self.max_workers} workers")

    def process_segment(self, segment_data):
        """Traite un segment audio et retourne le texte transcrit."""
        try:
            segment, segment_index, start_time, end_time = segment_data
            logging.debug(f"Segment {segment_index}/16: Tentative 1 de reconnaissance")
            
            # Utiliser un fichier temporaire pour le segment
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                segment_path = temp_file.name
                segment.export(segment_path, format="wav")
            
            # Créer un nouvel objet Recognizer pour chaque segment
            recognizer = sr.Recognizer()
            with sr.AudioFile(segment_path) as source:
                # Réduire l'utilisation de la mémoire en limitant la taille du buffer
                audio = recognizer.record(source, duration=min(45, end_time - start_time))
                text = recognizer.recognize_google(audio, language=self.language)
                
            # Supprimer le fichier temporaire
            try:
                os.unlink(segment_path)
                logging.debug(f"Segment {segment_index} supprimé")
            except Exception as e:
                logging.error(f"Erreur lors de la suppression du segment {segment_index}: {str(e)}")
            
            logging.debug(f"Segment {segment_index}/16: Reconnaissance réussie ({len(text)} caractères)")
            return segment_index, text.strip()
            
        except sr.UnknownValueError:
            logging.error(f"Segment {segment_index}/16: Audio incompréhensible")
            return segment_index, ""
            
        except sr.RequestError as e:
            logging.error(f"Segment {segment_index}/16: Erreur API ({str(e)})")
            return segment_index, ""
            
        except Exception as e:
            logging.error(f"Segment {segment_index}/16: Erreur inattendue ({str(e)})")
            return segment_index, ""
            
        finally:
            # S'assurer que le segment est libéré de la mémoire
            del segment
            gc.collect()

    def format_text(self, text):
        """Formate le texte pour une meilleure lisibilité"""
        # Ajouter une majuscule au début
        text = text.capitalize()
        
        # Ajouter un point à la fin si nécessaire
        if text and not text.endswith(('.', '!', '?')):
            text += '.'
        
        return text

    def convert_to_wav(self, audio_path):
        """Convertit le fichier audio en WAV"""
        # Créer un fichier temporaire avec extension .wav
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            wav_path = temp_file.name
        
        # Utiliser le chemin complet vers ffmpeg
        ffmpeg_cmd = '/opt/homebrew/bin/ffmpeg'
        
        # Construire la commande ffmpeg
        command = f'{ffmpeg_cmd} -i "{audio_path}" -acodec pcm_s16le -ac 1 -ar 44100 -y "{wav_path}"'
        logging.info(f"Conversion en WAV: {command}")
        
        # Exécuter la commande
        try:
            subprocess.run(command, shell=True, check=True, capture_output=True)
            return wav_path
        except subprocess.CalledProcessError as e:
            error_msg = f"Erreur lors de la conversion en WAV: {e.stderr.decode()}"
            logging.error(error_msg)
            self.error_occurred.emit(error_msg)
            raise RuntimeError(error_msg)

    def get_audio_duration(self, wav_path):
        """Obtient la durée du fichier audio en secondes"""
        try:
            with wave.open(wav_path, 'rb') as wav_file:
                frames = wav_file.getnframes()
                rate = wav_file.getframerate()
                duration = frames / float(rate)
                logging.info(f"Durée du fichier: {duration:.1f} secondes")
                return duration
        except Exception as e:
            error_msg = f"Erreur lors de la lecture de la durée: {str(e)}"
            logging.error(error_msg)
            self.error_occurred.emit(error_msg)
            raise

    def split_audio(self, audio):
        """Divise le fichier audio en segments"""
        try:
            duration_ms = len(audio)
            segment_duration_ms = 45 * 1000
            segments = []
            
            for start_ms in range(0, duration_ms, segment_duration_ms):
                end_ms = min(start_ms + segment_duration_ms, duration_ms)
                
                # Extraire le segment
                segment = audio[start_ms:end_ms]
                
                # Calculer les temps en secondes
                start_s = start_ms / 1000
                end_s = end_ms / 1000
                
                # Stocker le segment avec ses informations
                segments.append((segment, len(segments) + 1, start_s, end_s))
                
                logging.info(f"Segment créé: {start_s:.1f}s - {end_s:.1f}s")
                
            return segments
            
        except Exception as e:
            error_msg = f"Erreur lors de la division de l'audio: {str(e)}"
            logging.error(error_msg)
            raise

    def save_to_word(self, text, output_path):
        """Sauvegarde le texte dans un document Word"""
        try:
            doc = Document()
            
            # Ajouter un titre
            doc.add_heading('Transcription Audio', 0)
            
            # Ajouter la date et l'heure
            now = datetime.datetime.now()
            doc.add_paragraph(f'Généré le {now.strftime("%d/%m/%Y à %H:%M")}')
            
            # Ajouter une ligne de séparation
            doc.add_paragraph('_' * 50)
            
            # Ajouter le texte transcrit
            doc.add_paragraph(text)
            
            # Sauvegarder le document
            doc.save(output_path)
            logging.info(f"Document Word sauvegardé: {output_path}")
            
        except Exception as e:
            error_msg = f"Erreur lors de la sauvegarde du document Word: {str(e)}"
            logging.error(error_msg)
            self.error_occurred.emit(error_msg)
            raise

    def convert_to_text(self, audio_path, language='fr-FR'):
        """Convertit le fichier audio en texte."""
        self.language = language
        logging.info(f"Démarrage de la conversion du fichier: {audio_path}")
        logging.info(f"Langue sélectionnée: {language}")
        
        try:
            # Convertir en WAV avec les paramètres optimaux
            logging.info("Conversion du fichier en format WAV...")
            wav_path = self.convert_to_wav(audio_path)
            
            try:
                # Diviser l'audio en segments
                logging.info("Division du fichier audio en segments...")
                audio = AudioSegment.from_wav(wav_path)
                segments = self.split_audio(audio)
                logging.info(f"Nombre total de segments: {len(segments)}")
                
                # Libérer la mémoire du fichier WAV original
                del audio
                gc.collect()
                
                # Traitement parallèle avec un nombre limité de workers
                logging.info(f"Démarrage du traitement parallèle avec {self.max_workers} workers")
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    # Créer les futures
                    future_to_segment = {
                        executor.submit(self.process_segment, segment_data): segment_data[1]
                        for segment_data in segments
                    }
                    
                    # Traiter les résultats au fur et à mesure
                    results = []
                    for future in as_completed(future_to_segment):
                        try:
                            segment_index, text = future.result()
                            if text:  # Ne garder que les segments non vides
                                results.append((segment_index, text))
                                self.progress_updated.emit(segment_index, len(segments))
                                self.segment_completed.emit(f"Segment {segment_index}/{len(segments)} traité ({len(text)} caractères)")
                        except Exception as e:
                            logging.error(f"Erreur lors du traitement d'un segment: {str(e)}")
                            continue
                
                # Trier les résultats par index de segment
                results.sort(key=lambda x: x[0])
                
                # Joindre les textes
                text = "\n".join(text for _, text in results)
                
                # Nettoyer
                try:
                    os.unlink(wav_path)
                    logging.info("Fichier WAV temporaire supprimé")
                except Exception as e:
                    logging.error(f"Erreur lors de la suppression du fichier WAV: {str(e)}")
                
                return text
                
            except Exception as e:
                logging.error(f"Erreur lors de la conversion: {str(e)}")
                raise
                
        except Exception as e:
            logging.error(f"Erreur lors de la conversion: {str(e)}")
            raise
