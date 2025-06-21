"""
Control panel for the whisprd GUI using DearPyGui.
Provides buttons to start, stop, pause, and control the dictation system.
"""

import dearpygui.dearpygui as dpg
from typing import Optional, Any


class ControlPanel:
    """Control panel with start, stop, pause buttons using DearPyGui."""
    
    def __init__(self, main_window: Any) -> None:
        """Initialize the control panel."""
        self.main_window = main_window
        self.engine: Optional[Any] = None
        
        # Set up the panel
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """Create the control widgets."""
        # Title
        dpg.add_text("Dictation Controls")
        dpg.add_separator()
        
        # Control buttons
        with dpg.group():
            # Start button
            self.start_button = dpg.add_button(label="Start Engine", width=200, height=30,
                                             callback=self._on_start_clicked)
            
            # Stop button
            self.stop_button = dpg.add_button(label="Stop Engine", width=200, height=30,
                                            callback=self._on_stop_clicked)
            dpg.configure_item(self.stop_button, enabled=False)
            
            # Toggle dictation button
            self.toggle_button = dpg.add_button(label="Start Dictation", width=200, height=30,
                                              callback=self._on_toggle_clicked)
            dpg.configure_item(self.toggle_button, enabled=False)
            
            # Pause button
            self.pause_button = dpg.add_button(label="Pause", width=200, height=30,
                                             callback=self._on_pause_clicked)
            dpg.configure_item(self.pause_button, enabled=False)
        
        dpg.add_separator()
        
        # Info section
        with dpg.group():
            dpg.add_text("Hotkey: Ctrl+Shift+D")
            dpg.add_text("Command Mode: Say 'computer'")
            
            # Status info
            self.status_label = dpg.add_text("Engine not ready")
    
    def on_engine_ready(self, engine: Any) -> None:
        """Called when the engine is ready."""
        self.engine = engine
        dpg.configure_item(self.start_button, enabled=True)
        dpg.configure_item(self.status_label, default_value="Engine ready")
    
    def _on_start_clicked(self) -> None:
        """Handle start button click."""
        if self.engine and not self.engine.is_running:
            self.main_window.app.start_engine()
            self._update_button_states()
    
    def _on_stop_clicked(self) -> None:
        """Handle stop button click."""
        if self.engine and self.engine.is_running:
            self.main_window.app.stop_engine()
            self._update_button_states()
    
    def _on_toggle_clicked(self) -> None:
        """Handle toggle dictation button click."""
        if not self.engine:
            return
        
        if self.engine.is_dictating:
            self.engine.stop_dictation()
            dpg.configure_item(self.toggle_button, label="Start Dictation")
        else:
            self.engine.start_dictation()
            dpg.configure_item(self.toggle_button, label="Stop Dictation")
    
    def _on_pause_clicked(self) -> None:
        """Handle pause button click."""
        if not self.engine:
            return
        
        # Toggle pause state
        if hasattr(self.engine, 'is_paused'):
            if self.engine.is_paused:
                self.engine.resume()
                dpg.configure_item(self.pause_button, label="Pause")
            else:
                self.engine.pause()
                dpg.configure_item(self.pause_button, label="Resume")
    
    def _update_button_states(self) -> None:
        """Update button states based on engine status."""
        if not self.engine:
            return
        
        is_running = self.engine.is_running
        is_dictating = self.engine.is_dictating
        
        dpg.configure_item(self.start_button, enabled=not is_running)
        dpg.configure_item(self.stop_button, enabled=is_running)
        dpg.configure_item(self.toggle_button, enabled=is_running)
        dpg.configure_item(self.pause_button, enabled=is_running and is_dictating)
        
        if is_running:
            if is_dictating:
                dpg.configure_item(self.toggle_button, label="Stop Dictation")
                dpg.configure_item(self.status_label, default_value="Dictating")
            else:
                dpg.configure_item(self.toggle_button, label="Start Dictation")
                dpg.configure_item(self.status_label, default_value="Listening")
        else:
            dpg.configure_item(self.toggle_button, label="Start Dictation")
            dpg.configure_item(self.status_label, default_value="Engine stopped")
    
    def update_status(self, status: str) -> None:
        """Update the control panel status."""
        self._update_button_states() 