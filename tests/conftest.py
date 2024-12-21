import pytest
import os
import tempfile
import wave

@pytest.fixture
def test_audio_file():
    """Create a temporary WAV file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
        # Create a simple WAV file
        with wave.open(temp_file.name, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(44100)
            wf.writeframes(b'\x00' * 44100)  # 1 second of silence
        
        yield temp_file.name
        # Cleanup
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)

@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for output files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir
