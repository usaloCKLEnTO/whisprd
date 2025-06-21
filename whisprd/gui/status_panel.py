"""
Status panel for the whisprd GUI using DearPyGui.
Displays real-time status information and statistics.
"""

import dearpygui.dearpygui as dpg
from typing import Optional, Dict, Any
from datetime import datetime


class StatusPanel:
    """Status panel showing engine status and statistics using DearPyGui."""
    
    def __init__(self, main_window: Any) -> None:
        """Initialize the status panel."""
        self.main_window = main_window
        self.engine: Optional[Any] = None
        
        # Set up the panel
        self._create_widgets()
        
        # Set up timer for updates
        self.update_timer = None
    
    def _create_widgets(self) -> None:
        """Create the status widgets."""
        # Title
        dpg.add_text("Engine Status")
        dpg.add_separator()
        
        # Status section
        dpg.add_text("Status Information:")
        
        # Status grid
        with dpg.group():
            # Engine status
            dpg.add_text("Engine:")
            self.status_engine = dpg.add_text("Not running")
            
            dpg.add_text("Dictation:")
            self.status_dictation = dpg.add_text("Inactive")
            
            dpg.add_text("Audio Queue:")
            self.status_audio_queue = dpg.add_text("0")
            
            dpg.add_text("Transcription Queue:")
            self.status_transcription_queue = dpg.add_text("0")
        
        dpg.add_separator()
        
        # Statistics section
        dpg.add_text("Statistics:")
        
        # Statistics grid
        with dpg.group():
            # Start time
            dpg.add_text("Start Time:")
            self.stats_start_time = dpg.add_text("N/A")
            
            # Uptime
            dpg.add_text("Uptime:")
            self.stats_uptime = dpg.add_text("N/A")
            
            # Transcriptions
            dpg.add_text("Transcriptions:")
            self.stats_transcriptions = dpg.add_text("0")
            
            # Commands
            dpg.add_text("Commands:")
            self.stats_commands = dpg.add_text("0")
            
            # Characters
            dpg.add_text("Characters:")
            self.stats_characters = dpg.add_text("0")
            
            # Errors
            dpg.add_text("Errors:")
            self.stats_errors = dpg.add_text("0")
    
    def on_engine_ready(self, engine: Any) -> None:
        """Called when the engine is ready."""
        self.engine = engine
        self._start_updates()
    
    def _start_updates(self) -> None:
        """Start periodic status updates."""
        # DearPyGui doesn't have a built-in timer, so we'll use a callback approach
        # The updates will be triggered by the main window's status updates
        pass
    
    def _update_status(self) -> None:
        """Update the status display."""
        if not self.engine:
            return
        
        try:
            status = self.engine.get_status()
            
            # Update status
            self._update_status_value("status_engine", "Running" if status['is_running'] else "Not running")
            self._update_status_value("status_dictation", "Active" if status['is_dictating'] else "Inactive")
            self._update_status_value("status_audio_queue", str(status['audio_queue_size']))
            self._update_status_value("status_transcription_queue", str(status['transcription_queue_size']))
            
            # Update statistics
            stats = status['stats']
            
            # Start time
            if stats['start_time']:
                start_time = stats['start_time'].strftime("%H:%M:%S")
                self._update_stats_value("stats_start_time", start_time)
                
                # Uptime
                uptime = datetime.now() - stats['start_time']
                uptime_str = str(uptime).split('.')[0]  # Remove microseconds
                self._update_stats_value("stats_uptime", uptime_str)
            else:
                self._update_stats_value("stats_start_time", "N/A")
                self._update_stats_value("stats_uptime", "N/A")
            
            self._update_stats_value("stats_transcriptions", str(stats['total_transcriptions']))
            self._update_stats_value("stats_commands", str(stats['total_commands']))
            self._update_stats_value("stats_characters", str(stats['total_characters']))
            self._update_stats_value("stats_errors", str(stats['errors']))
            
        except Exception as e:
            # Log error but continue updates
            pass
    
    def _update_status_value(self, item_id: str, value: str) -> None:
        """Update a status value."""
        dpg.configure_item(item_id, default_value=value)
    
    def _update_stats_value(self, item_id: str, value: str) -> None:
        """Update a statistics value."""
        dpg.configure_item(item_id, default_value=value)
    
    def update_status(self, status: str) -> None:
        """Update the status panel."""
        # Trigger a status update when called
        self._update_status() 