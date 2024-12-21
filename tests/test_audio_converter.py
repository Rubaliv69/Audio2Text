import pytest
import os
from src.audio_converter import AudioConverter

@pytest.fixture
def audio_converter():
    return AudioConverter()

def test_supported_formats():
    converter = AudioConverter()
    assert hasattr(converter, 'supported_formats')
    assert isinstance(converter.supported_formats, list)
    assert len(converter.supported_formats) > 0

def test_convert_audio_invalid_input():
    converter = AudioConverter()
    with pytest.raises(FileNotFoundError):
        converter.convert_audio("nonexistent_file.mp3")

def test_convert_audio_invalid_format():
    converter = AudioConverter()
    with pytest.raises(ValueError):
        converter.convert_audio("test.xyz")  # Invalid format

def test_get_duration():
    converter = AudioConverter()
    # Create a small test audio file or use a fixture
    with pytest.raises(FileNotFoundError):
        converter.get_duration("nonexistent_file.mp3")
