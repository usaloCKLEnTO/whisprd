"""
Main window for the whisprd GUI application using DearPyGui.
"""

import dearpygui.dearpygui as dpg
from typing import Optional, Dict, Any, List
from .config_panel import ConfigPanel
from .status_panel import StatusPanel
from .transcription_panel import TranscriptionPanel
from .control_panel import ControlPanel


class WhisprdMainWindow:
    """Main window for the whisprd GUI application using DearPyGui."""
    
    def __init__(self, app: Any) -> None:
        """Initialize the main window."""
        self.app = app
        self.engine: Optional[Any] = None
        
        # Create the main window
        self._create_window()
    
    def _create_window(self) -> None:
        """Create the main window layout."""
        # Create main window
        with dpg.window(label="Whisprd - Real-time Dictation System", tag="main_window", 
                       width=1200, height=800, no_close=True, no_collapse=True):
            
            # Create header with status indicator
            with dpg.group(horizontal=True):
                dpg.add_text("Whisprd")
                dpg.add_spacer(width=20)
                dpg.add_text("Initializing...", tag="status_indicator")
            
            dpg.add_separator()
            
            # Create main layout with two columns
            with dpg.group(horizontal=True):
                
                # Left panel (controls and status)
                with dpg.child_window(width=400, height=700):
                    self.control_panel = ControlPanel(self)
                    dpg.add_separator()
                    self.status_panel = StatusPanel(self)
                
                # Right panel (transcription and config)
                with dpg.child_window(width=780, height=700):
                    self.transcription_panel = TranscriptionPanel(self)
                    dpg.add_separator()
                    self.config_panel = ConfigPanel(self)
    
    def on_engine_ready(self, engine: Any) -> None:
        """Called when the engine is ready."""
        self.engine = engine
        self.control_panel.on_engine_ready(engine)
        self.status_panel.on_engine_ready(engine)
        self.config_panel.on_engine_ready(engine)
        self.update_status("Ready")
    
    def update_status(self, status: str) -> None:
        """Update the status indicator."""
        if status == "dictating":
            dpg.configure_item("status_indicator", default_value="🎤 Dictating")
        elif status == "listening":
            dpg.configure_item("status_indicator", default_value="👂 Listening")
        elif status == "ready":
            dpg.configure_item("status_indicator", default_value="✅ Ready")
        elif status == "stopped":
            dpg.configure_item("status_indicator", default_value="⏹️ Stopped")
        else:
            dpg.configure_item("status_indicator", default_value=status)
    
    def add_transcription(self, original_text: str, clean_text: str, matches: List[Dict[str, Any]]) -> None:
        """Add a transcription to the transcription panel."""
        self.transcription_panel.add_transcription(original_text, clean_text, matches)
    
    def get_engine(self) -> Optional[Any]:
        """Get the dictation engine."""
        return self.engine 