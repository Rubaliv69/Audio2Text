import os
import sys
import pytest
import tempfile
from pathlib import Path
from pydub import AudioSegment

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.audio_converter import AudioConverter

@pytest.fixture
def audio_converter():
    return AudioConverter()

@pytest.fixture
def temp_wav_file():
    # Créer un fichier audio WAV temporaire pour les tests
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
        audio = AudioSegment.silent(duration=1000)  # 1 seconde de silence
        audio.export(temp_file.name, format='wav')
        yield temp_file.name
    os.unlink(temp_file.name)

def test_audio_converter_initialization(audio_converter):
    assert audio_converter is not None
    assert audio_converter.language == 'fr-FR'
    assert audio_converter.max_workers > 0

def test_supported_formats(audio_converter):
    assert len(audio_converter.supported_formats) > 0
    assert '.wav' in audio_converter.supported_formats
    assert '.mp3' in audio_converter.supported_formats

def test_convert_audio_invalid_input():
    converter = AudioConverter()
    with pytest.raises(Exception) as excinfo:
        converter.convert_to_wav("nonexistent_file.mp3")
    assert "No such file or directory" in str(excinfo.value)

def test_convert_audio_invalid_format():
    converter = AudioConverter()
    with tempfile.NamedTemporaryFile(suffix='.xyz') as temp_file:
        with pytest.raises(Exception) as excinfo:
            converter.convert_to_wav(temp_file.name)
        assert "Invalid data found when processing input" in str(excinfo.value)

def test_split_audio(audio_converter, temp_wav_file):
    # Charger l'audio
    audio = AudioSegment.from_wav(temp_wav_file)
    
    # Tester la division en segments
    segments = audio_converter.split_audio(audio)
    
    assert isinstance(segments, list)
    assert len(segments) > 0
    for segment, index, start, end in segments:
        assert isinstance(segment, AudioSegment)
        assert isinstance(index, int)
        assert index > 0
        assert isinstance(start, float)
        assert isinstance(end, float)
        assert end > start

def test_process_segment(audio_converter, temp_wav_file):
    # Charger l'audio
    audio = AudioSegment.from_wav(temp_wav_file)
    
    # Créer un segment de test
    segment_data = (audio, 1, 0.0, 1.0)
    
    # Tester le traitement du segment
    result = audio_converter.process_segment(segment_data)
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert isinstance(result[0], int)
    assert isinstance(result[1], str)

def test_format_text(audio_converter):
    # Test de formatage de texte
    test_text = "hello world"
    formatted = audio_converter.format_text(test_text)
    assert isinstance(formatted, str)
    assert formatted[0].isupper()  # Première lettre en majuscule

def test_language_setting(audio_converter):
    # Test du paramètre de langue
    test_language = 'fr-FR'
    audio_converter.language = test_language
    assert audio_converter.language == test_language

def test_max_workers_setting(audio_converter):
    # Test du paramètre max_workers
    assert audio_converter.max_workers > 0
    assert isinstance(audio_converter.max_workers, int)

def test_get_duration():
    converter = AudioConverter()
    with pytest.raises(FileNotFoundError) as excinfo:
        converter.get_duration("nonexistent_file.mp3")
    assert "n'existe pas" in str(excinfo.value)
