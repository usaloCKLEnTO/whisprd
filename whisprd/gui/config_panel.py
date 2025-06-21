"""
Configuration panel for the whisprd GUI using DearPyGui.
Allows users to view and modify configuration settings.
"""

import dearpygui.dearpygui as dpg
from typing import Optional, Dict, Any
import yaml
import os


class ConfigPanel:
    """Configuration panel for viewing and editing settings using DearPyGui."""
    
    def __init__(self, main_window: Any) -> None:
        """Initialize the configuration panel."""
        self.main_window = main_window
        self.engine: Optional[Any] = None
        self.config: Optional[Any] = None
        
        # Set up the panel
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """Create the configuration widgets."""
        # Title and controls
        with dpg.group(horizontal=True):
            dpg.add_text("Configuration")
            dpg.add_spacer(width=20)
            
            # Reload button
            dpg.add_button(label="Reload", callback=self._on_reload_clicked, width=60)
            
            # Save button
            dpg.add_button(label="Save", callback=self._on_save_clicked, width=60)
        
        dpg.add_separator()
        
        # Create tab bar for different config sections
        with dpg.tab_bar():
            # Audio tab
            with dpg.tab(label="Audio"):
                self._create_audio_tab()
            
            # Whisper tab
            with dpg.tab(label="Whisper"):
                self._create_whisper_tab()
            
            # Whisprd tab
            with dpg.tab(label="Whisprd"):
                self._create_whisprd_tab()
            
            # Commands tab
            with dpg.tab(label="Commands"):
                self._create_commands_tab()
            
            # Output tab
            with dpg.tab(label="Output"):
                self._create_output_tab()
            
            # Performance tab
            with dpg.tab(label="Performance"):
                self._create_performance_tab()
    
    def _create_audio_tab(self) -> None:
        """Create the audio configuration tab."""
        with dpg.group():
            # Sample rate
            with dpg.group(horizontal=True):
                dpg.add_text("Sample Rate:")
                self.sample_rate_spin = dpg.add_input_int(
                    default_value=16000, min_value=8000, max_value=48000, step=1000
                )
            
            # Channels
            with dpg.group(horizontal=True):
                dpg.add_text("Channels:")
                self.channels_spin = dpg.add_input_int(
                    default_value=1, min_value=1, max_value=2, step=1
                )
            
            # Buffer size
            with dpg.group(horizontal=True):
                dpg.add_text("Buffer Size:")
                self.buffer_spin = dpg.add_input_int(
                    default_value=8000, min_value=1000, max_value=16000, step=1000
                )
            
            # Device selection
            with dpg.group(horizontal=True):
                dpg.add_text("Audio Device:")
                self.device_combo = dpg.add_combo(
                    items=["Default Device"], default_value="Default Device"
                )
    
    def _create_whisper_tab(self) -> None:
        """Create the Whisper configuration tab."""
        with dpg.group():
            # Model size
            with dpg.group(horizontal=True):
                dpg.add_text("Model Size:")
                self.model_combo = dpg.add_combo(
                    items=["tiny", "base", "small", "medium", "large"],
                    default_value="small"
                )
            
            # Language
            with dpg.group(horizontal=True):
                dpg.add_text("Language:")
                self.language_entry = dpg.add_input_text(default_value="en")
            
            # Beam size
            with dpg.group(horizontal=True):
                dpg.add_text("Beam Size:")
                self.beam_spin = dpg.add_input_int(
                    default_value=5, min_value=1, max_value=10, step=1
                )
            
            # Temperature
            with dpg.group(horizontal=True):
                dpg.add_text("Temperature:")
                self.temp_spin = dpg.add_input_float(
                    default_value=0.0, min_value=0.0, max_value=2.0
                )
            
            # CUDA settings
            with dpg.group(horizontal=True):
                dpg.add_text("Use CUDA:")
                self.cuda_switch = dpg.add_checkbox(default_value=True)
    
    def _create_whisprd_tab(self) -> None:
        """Create the Whisprd configuration tab."""
        with dpg.group():
            # Confidence threshold
            with dpg.group(horizontal=True):
                dpg.add_text("Confidence Threshold:")
                self.conf_scale = dpg.add_slider_float(
                    default_value=0.8, min_value=0.0, max_value=1.0
                )
            
            # Command mode word
            with dpg.group(horizontal=True):
                dpg.add_text("Command Word:")
                self.cmd_entry = dpg.add_input_text(default_value="computer")
            
            # Auto punctuation
            with dpg.group(horizontal=True):
                dpg.add_text("Auto Punctuation:")
                self.punct_switch = dpg.add_checkbox(default_value=True)
            
            # Pause duration
            with dpg.group(horizontal=True):
                dpg.add_text("Pause Duration (s):")
                self.pause_spin = dpg.add_input_float(
                    default_value=1.0, min_value=0.5, max_value=5.0, step=0.1
                )
    
    def _create_commands_tab(self) -> None:
        """Create the commands configuration tab."""
        with dpg.group():
            dpg.add_text("Voice Commands")
            
            # Commands text area
            self.commands_text = dpg.add_input_text(
                default_value="",
                multiline=True,
                height=200
            )
    
    def _create_output_tab(self) -> None:
        """Create the output configuration tab."""
        with dpg.group():
            # Save to file
            with dpg.group(horizontal=True):
                dpg.add_text("Save to File:")
                self.save_switch = dpg.add_checkbox(default_value=True)
            
            # Transcript file
            with dpg.group(horizontal=True):
                dpg.add_text("Transcript File:")
                self.file_entry = dpg.add_input_text(default_value="~/whisprd_transcript.txt")
            
            # Console output
            with dpg.group(horizontal=True):
                dpg.add_text("Console Output:")
                self.console_switch = dpg.add_checkbox(default_value=True)
            
            # Inject keystrokes
            with dpg.group(horizontal=True):
                dpg.add_text("Inject Keystrokes:")
                self.inject_switch = dpg.add_checkbox(default_value=True)
    
    def _create_performance_tab(self) -> None:
        """Create the performance configuration tab."""
        with dpg.group():
            # Transcription threads
            with dpg.group(horizontal=True):
                dpg.add_text("Transcription Threads:")
                self.threads_spin = dpg.add_input_int(
                    default_value=2, min_value=1, max_value=8, step=1
                )
            
            # Audio buffer seconds
            with dpg.group(horizontal=True):
                dpg.add_text("Audio Buffer (s):")
                self.buffer_sec_spin = dpg.add_input_float(
                    default_value=1.0, min_value=0.5, max_value=5.0, step=0.1
                )
            
            # Max latency
            with dpg.group(horizontal=True):
                dpg.add_text("Max Latency (s):")
                self.latency_spin = dpg.add_input_float(
                    default_value=2.0, min_value=0.5, max_value=10.0, step=0.1
                )
            
            # GPU memory fraction
            with dpg.group(horizontal=True):
                dpg.add_text("GPU Memory Fraction:")
                self.gpu_scale = dpg.add_slider_float(
                    default_value=0.8, min_value=0.1, max_value=1.0
                )
    
    def on_engine_ready(self, engine: Any) -> None:
        """Called when the engine is ready."""
        self.engine = engine
        self.config = engine.config
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration into the UI."""
        if not self.config:
            return
        
        try:
            # Audio settings
            audio_config = self.config.get_audio_config()
            dpg.configure_item(self.sample_rate_spin, default_value=audio_config.get('sample_rate', 16000))
            dpg.configure_item(self.channels_spin, default_value=audio_config.get('channels', 1))
            dpg.configure_item(self.buffer_spin, default_value=audio_config.get('buffer_size', 8000))
            
            # Whisper settings
            whisper_config = self.config.get_whisper_config()
            dpg.configure_item(self.model_combo, default_value=whisper_config.get('model_size', 'small'))
            dpg.configure_item(self.language_entry, default_value=whisper_config.get('language', 'en'))
            dpg.configure_item(self.beam_spin, default_value=whisper_config.get('beam_size', 5))
            dpg.configure_item(self.temp_spin, default_value=whisper_config.get('temperature', 0.0))
            dpg.configure_item(self.cuda_switch, default_value=whisper_config.get('use_cuda', True))
            
            # Whisprd settings
            whisprd_config = self.config.get_whisprd_config()
            dpg.configure_item(self.conf_scale, default_value=whisprd_config.get('confidence_threshold', 0.8))
            dpg.configure_item(self.cmd_entry, default_value=whisprd_config.get('command_mode_word', 'computer'))
            dpg.configure_item(self.punct_switch, default_value=whisprd_config.get('auto_punctuation', True))
            dpg.configure_item(self.pause_spin, default_value=whisprd_config.get('pause_duration', 1.0))
            
            # Commands
            commands = self.config.get_commands()
            commands_text = yaml.dump(commands, default_flow_style=False)
            dpg.configure_item(self.commands_text, default_value=commands_text)
            
            # Output settings
            output_config = self.config.get_output_config()
            dpg.configure_item(self.save_switch, default_value=output_config.get('save_to_file', True))
            dpg.configure_item(self.file_entry, default_value=output_config.get('transcript_file', '~/whisprd_transcript.txt'))
            dpg.configure_item(self.console_switch, default_value=output_config.get('console_output', True))
            dpg.configure_item(self.inject_switch, default_value=output_config.get('inject_keystrokes', True))
            
            # Performance settings
            perf_config = self.config.get_performance_config()
            dpg.configure_item(self.threads_spin, default_value=perf_config.get('transcription_threads', 2))
            dpg.configure_item(self.buffer_sec_spin, default_value=perf_config.get('audio_buffer_seconds', 1.0))
            dpg.configure_item(self.latency_spin, default_value=perf_config.get('max_latency', 2.0))
            dpg.configure_item(self.gpu_scale, default_value=perf_config.get('gpu_memory_fraction', 0.8))
            
        except Exception as e:
            # Show error dialog
            with dpg.window(label="Configuration Error", modal=True, no_close=True, width=400, height=200):
                dpg.add_text(f"Failed to load configuration:\n{str(e)}")
                dpg.add_separator()
                dpg.add_button(label="OK", callback=lambda: dpg.delete_item(dpg.last_item_container()))
    
    def _on_reload_clicked(self) -> None:
        """Handle reload button click."""
        if self.engine:
            try:
                self.engine.reload_config()
                self.config = self.engine.config
                self._load_config()
                
                # Show success message
                with dpg.window(label="Success", modal=True, no_close=True, width=300, height=150):
                    dpg.add_text("Configuration has been reloaded from file.")
                    dpg.add_separator()
                    dpg.add_button(label="OK", callback=lambda: dpg.delete_item(dpg.last_item_container()))
                
            except Exception as e:
                # Show error message
                with dpg.window(label="Error", modal=True, no_close=True, width=300, height=150):
                    dpg.add_text(f"Failed to reload configuration:\n{str(e)}")
                    dpg.add_separator()
                    dpg.add_button(label="OK", callback=lambda: dpg.delete_item(dpg.last_item_container()))
    
    def _on_save_clicked(self) -> None:
        """Handle save button click."""
        # This would require implementing configuration saving
        # For now, just show a message
        with dpg.window(label="Info", modal=True, no_close=True, width=300, height=150):
            dpg.add_text("Configuration saving is not yet implemented.\nUse the reload button to reload from file.")
            dpg.add_separator()
            dpg.add_button(label="OK", callback=lambda: dpg.delete_item(dpg.last_item_container()))
    
    def update_status(self, status: str) -> None:
        """Update the configuration panel status."""
        # This method is called from the main window
        # No specific updates needed for config panel
        pass 