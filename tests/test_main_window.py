import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
import sys
import os

# Ajouter le répertoire parent au chemin Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main_window import MainWindow

@pytest.fixture
def app():
    """Create a Qt application instance for testing."""
    return QApplication(sys.argv)

@pytest.fixture
def main_window(app):
    """Create the main window instance for testing."""
    window = MainWindow()
    yield window
    window.close()

def test_window_title(main_window):
    """Test if the window has the correct title."""
    assert "Audio2Text" in main_window.windowTitle()

def test_initial_state(main_window):
    """Test the initial state of the main window."""
    assert main_window.select_button is not None
    assert main_window.select_button.isEnabled()  # Le bouton de sélection devrait être activé

def test_file_selection(main_window):
    """Test file selection behavior."""
    assert hasattr(main_window, 'select_file')  # Vérifie que la méthode existe
    assert callable(main_window.select_file)  # Vérifie que c'est une méthode appelable
