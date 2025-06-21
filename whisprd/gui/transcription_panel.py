"""
Transcription panel for the whisprd GUI using DearPyGui.
Displays real-time transcription results and history.
"""

import dearpygui.dearpygui as dpg
from typing import Optional, Dict, Any, List
from datetime import datetime


class TranscriptionPanel:
    """Transcription panel showing real-time results and history using DearPyGui."""
    
    def __init__(self, main_window: Any) -> None:
        """Initialize the transcription panel."""
        self.main_window = main_window
        self.engine: Optional[Any] = None
        
        # Transcription history
        self.transcriptions: List[Dict[str, Any]] = []
        self.max_transcriptions = 100  # Keep last 100 transcriptions
        
        # Set up the panel
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """Create the transcription widgets."""
        # Title and controls
        with dpg.group(horizontal=True):
            dpg.add_text("Live Transcriptions")
            dpg.add_spacer(width=20)
            
            # Clear button
            dpg.add_button(label="Clear", callback=self._on_clear_clicked, width=60)
            
            # Save button
            dpg.add_button(label="Save", callback=self._on_save_clicked, width=60)
        
        dpg.add_separator()
        
        # Current transcription display
        dpg.add_text("Current:")
        
        # Current text area
        self.current_text = dpg.add_input_text(
            default_value="",
            readonly=True,
            multiline=True,
            height=80,
            width=-1
        )
        
        dpg.add_separator()
        
        # History section
        dpg.add_text("History:")
        
        # History list
        with dpg.child_window(height=300, width=-1):
            self.history_group = dpg.add_group()
    
    def on_engine_ready(self, engine: Any) -> None:
        """Called when the engine is ready."""
        self.engine = engine
    
    def add_transcription(self, original_text: str, clean_text: str, matches: List[Dict[str, Any]]) -> None:
        """Add a transcription to the panel."""
        # Add to history
        timestamp = datetime.now()
        transcription = {
            'timestamp': timestamp,
            'original': original_text,
            'clean': clean_text,
            'matches': matches
        }
        
        self.transcriptions.append(transcription)
        
        # Keep only the last max_transcriptions
        if len(self.transcriptions) > self.max_transcriptions:
            self.transcriptions.pop(0)
        
        # Update current text
        self._update_current_text(clean_text)
        
        # Add to history list
        self._add_to_history_list(transcription)
    
    def _update_current_text(self, text: str) -> None:
        """Update the current transcription text."""
        dpg.configure_item(self.current_text, default_value=text)
    
    def _add_to_history_list(self, transcription: Dict[str, Any]) -> None:
        """Add a transcription to the history list."""
        # Create a new group for this transcription
        with dpg.group(parent=self.history_group):
            # Time and text
            time_str = transcription['timestamp'].strftime("%H:%M:%S")
            dpg.add_text(time_str)
            
            text_label = dpg.add_text(transcription['clean'])
            
            # Add original text if different
            if transcription['original'] != transcription['clean']:
                original_text = f"Original: {transcription['original']}"
                dpg.add_text(original_text)
            
            # Add commands if any
            if transcription['matches']:
                commands = [match['phrase'] for match in transcription['matches']]
                commands_text = f"Commands: {', '.join(commands)}"
                dpg.add_text(commands_text)
            
            dpg.add_separator()
    
    def _on_clear_clicked(self) -> None:
        """Handle clear button click."""
        # Clear current text
        dpg.configure_item(self.current_text, default_value="")
        
        # Clear history
        self.transcriptions.clear()
        
        # Clear history display
        dpg.delete_item(self.history_group, children_only=True)
    
    def _on_save_clicked(self) -> None:
        """Handle save button click."""
        if not self.transcriptions:
            return
        
        # Create file dialog
        with dpg.file_dialog(label="Save Transcriptions", callback=self._on_file_selected,
                           width=600, height=400, default_path="whisprd_transcriptions.txt"):
            dpg.add_file_extension(".txt", color=(0, 255, 0, 255))
            dpg.add_file_extension(".log", color=(0, 255, 0, 255))
    
    def _on_file_selected(self, sender: int, app_data: Dict[str, Any]) -> None:
        """Handle file selection for saving."""
        filename = app_data["file_path_name"]
        self._save_transcriptions(filename)
    
    def _save_transcriptions(self, filename: str) -> None:
        """Save transcriptions to file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("Whisprd Transcriptions\n")
                f.write("=" * 50 + "\n\n")
                
                for transcription in reversed(self.transcriptions):  # Most recent first
                    timestamp = transcription['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
                    f.write(f"[{timestamp}]\n")
                    f.write(f"Text: {transcription['clean']}\n")
                    
                    if transcription['original'] != transcription['clean']:
                        f.write(f"Original: {transcription['original']}\n")
                    
                    if transcription['matches']:
                        commands = [match['phrase'] for match in transcription['matches']]
                        f.write(f"Commands: {', '.join(commands)}\n")
                    
                    f.write("\n")
            
            # Show success message
            with dpg.window(label="Success", modal=True, no_close=True, width=300, height=150):
                dpg.add_text(f"Transcriptions saved to:\n{filename}")
                dpg.add_separator()
                dpg.add_button(label="OK", callback=lambda: dpg.delete_item(dpg.last_item_container()))
                
        except Exception as e:
            # Show error message
            with dpg.window(label="Error", modal=True, no_close=True, width=300, height=150):
                dpg.add_text(f"Failed to save transcriptions:\n{str(e)}")
                dpg.add_separator()
                dpg.add_button(label="OK", callback=lambda: dpg.delete_item(dpg.last_item_container()))
    
    def update_status(self, status: str) -> None:
        """Update the transcription panel."""
        # This method is called from the main window
        # No specific updates needed for transcription panel
        pass 