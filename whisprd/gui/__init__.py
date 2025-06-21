"""
GUI module for the whisprd system using DearPyGui.
Provides a modern, cross-platform graphical interface.
"""

from .main_window import WhisprdMainWindow
from .control_panel import ControlPanel
from .status_panel import StatusPanel
from .transcription_panel import TranscriptionPanel
from .config_panel import ConfigPanel

__all__ = [
    'WhisprdMainWindow',
    'ControlPanel', 
    'StatusPanel',
    'TranscriptionPanel',
    'ConfigPanel'
] 