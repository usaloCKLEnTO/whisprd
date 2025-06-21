#!/usr/bin/env python3
"""
Demo script for the DearPyGui-based whisprd GUI.
This demonstrates the GUI without requiring the full engine.
"""

import sys
import os
import threading
import time
import random
from typing import Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import dearpygui.dearpygui as dpg


class MockEngine:
    """Mock engine for demonstration purposes."""
    
    def __init__(self):
        self.is_running = False
        self.is_dictating = False
        self.is_paused = False
        self.config = MockConfig()
    
    def start(self):
        self.is_running = True
    
    def stop(self):
        self.is_running = False
        self.is_dictating = False
    
    def start_dictation(self):
        self.is_dictating = True
    
    def stop_dictation(self):
        self.is_dictating = False
    
    def pause(self):
        self.is_paused = True
    
    def resume(self):
        self.is_paused = False
    
    def get_status(self):
        return {
            'is_running': self.is_running,
            'is_dictating': self.is_dictating,
            'audio_queue_size': random.randint(0, 5),
            'transcription_queue_size': random.randint(0, 3),
            'stats': {
                'start_time': time.time() - 3600 if self.is_running else None,
                'total_transcriptions': random.randint(10, 100),
                'total_commands': random.randint(5, 20),
                'total_characters': random.randint(500, 2000),
                'errors': random.randint(0, 3)
            }
        }


class MockConfig:
    """Mock configuration for demonstration."""
    
    def get_audio_config(self):
        return {
            'sample_rate': 16000,
            'channels': 1,
            'buffer_size': 8000
        }
    
    def get_whisper_config(self):
        return {
            'model_size': 'small',
            'language': 'en',
            'beam_size': 5,
            'temperature': 0.0,
            'use_cuda': True
        }
    
    def get_whisprd_config(self):
        return {
            'confidence_threshold': 0.8,
            'command_mode_word': 'computer',
            'auto_punctuation': True,
            'pause_duration': 1.0
        }
    
    def get_commands(self):
        return {
            'new line': 'KEY_ENTER',
            'period': 'KEY_DOT',
            'comma': 'KEY_COMMA',
            'backspace': 'KEY_BACKSPACE'
        }
    
    def get_output_config(self):
        return {
            'save_to_file': True,
            'transcript_file': '~/whisprd_transcript.txt',
            'console_output': True,
            'inject_keystrokes': True
        }
    
    def get_performance_config(self):
        return {
            'transcription_threads': 2,
            'audio_buffer_seconds': 1.0,
            'max_latency': 2.0,
            'gpu_memory_fraction': 0.8
        }


class DemoGUI:
    """Demo GUI application."""
    
    def _detect_scaling(self, manual_scale: Optional[float] = None, auto_scale_multiplier: float = 1.1) -> float:
        if manual_scale is not None:
            return manual_scale
        
        detected_scale = 1.0
        
        # 1. Check GDK_SCALE
        gdk_scale = os.environ.get("GDK_SCALE")
        if gdk_scale:
            try:
                detected_scale = float(gdk_scale)
            except Exception:
                pass
        
        # 2. Check gsettings text-scaling-factor
        if detected_scale == 1.0:
            try:
                import subprocess
                out = subprocess.check_output([
                    "gsettings", "get", "org.gnome.desktop.interface", "text-scaling-factor"
                ], encoding="utf-8").strip()
                if out and float(out) != 1.0:
                    detected_scale = float(out)
            except Exception:
                pass
        
        # 3. Check for automatic scaling (scaling-factor = 0)
        if detected_scale == 1.0:
            try:
                import subprocess
                scaling_factor = subprocess.check_output([
                    "gsettings", "get", "org.gnome.desktop.interface", "scaling-factor"
                ], encoding="utf-8").strip()
                
                # If scaling-factor is 0, it means automatic scaling is enabled
                if scaling_factor == "0":
                    # Try to detect scaling from display properties
                    detected_scale = self._detect_display_scaling()
            except Exception:
                pass
        
        # 4. Fallback: try to detect from display properties
        if detected_scale == 1.0:
            detected_scale = self._detect_display_scaling()
        
        # Apply the autoscaling multiplier
        return detected_scale * auto_scale_multiplier
    
    def _detect_display_scaling(self) -> float:
        """Detect scaling from display properties using xrandr."""
        try:
            import subprocess
            import re
            
            # Get xrandr output
            output = subprocess.check_output(['xrandr', '--query'], text=True)
            lines = output.split('\n')
            
            # Find primary display
            for line in lines:
                if 'connected' in line and 'primary' in line:
                    match = re.search(r'(\d+)x(\d+)', line)
                    if match:
                        physical_width = int(match.group(1))
                        physical_height = int(match.group(2))
                        # Find current logical resolution (marked with *)
                        for next_line in lines:
                            if '*' in next_line:
                                res_match = re.search(r'(\d+)x(\d+)', next_line)
                                if res_match:
                                    logical_width = int(res_match.group(1))
                                    logical_height = int(res_match.group(2))
                                    scale_x = physical_width / logical_width
                                    scale_y = physical_height / logical_height
                                    avg_scale = (scale_x + scale_y) / 2
                                    if 0.5 <= avg_scale <= 3.0:
                                        return avg_scale
                        break
        except Exception:
            pass
        return 1.0
    
    def __init__(self, scale: Optional[float] = None, auto_scale_multiplier: float = 1.1):
        # Initialize DearPyGui
        scale_factor = self._detect_scaling(scale, auto_scale_multiplier)
        dpg.create_context()
        dpg.set_global_font_scale(scale_factor)
        dpg.create_viewport(title="Whisprd Demo - DearPyGui Interface", width=1200, height=800)
        dpg.setup_dearpygui()
        
        # Create mock engine
        self.engine = MockEngine()
        
        # Create main window
        self._create_window()
        
        # Start demo thread
        self.demo_thread = threading.Thread(target=self._demo_loop, daemon=True)
        self.demo_thread.start()
    
    def _create_window(self):
        """Create the main window layout."""
        # Create main window
        with dpg.window(label="Whisprd Demo - Real-time Dictation System", tag="main_window", 
                       width=1200, height=800, no_close=True, no_collapse=True):
            
            # Create header with status indicator
            with dpg.group(horizontal=True):
                dpg.add_text("Whisprd Demo")
                dpg.add_spacer(width=20)
                dpg.add_text("Initializing...", tag="status_indicator")
            
            dpg.add_separator()
            
            # Create main layout with two columns
            with dpg.group(horizontal=True):
                
                # Left panel (controls and status)
                with dpg.child_window(width=400, height=700):
                    self._create_control_panel()
                    dpg.add_separator()
                    self._create_status_panel()
                
                # Right panel (transcription and config)
                with dpg.child_window(width=780, height=700):
                    self._create_transcription_panel()
                    dpg.add_separator()
                    self._create_config_panel()
    
    def _create_control_panel(self):
        """Create the control panel."""
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
    
    def _create_status_panel(self):
        """Create the status panel."""
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
    
    def _create_transcription_panel(self):
        """Create the transcription panel."""
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
    
    def _create_config_panel(self):
        """Create the configuration panel."""
        # Title and controls
        with dpg.group(horizontal=True):
            dpg.add_text("Configuration")
            dpg.add_spacer(width=20)
            
            # Reload button
            dpg.add_button(label="Reload", callback=self._on_reload_clicked, width=60)
            
            # Save button
            dpg.add_button(label="Save", callback=self._on_save_config_clicked, width=60)
        
        dpg.add_separator()
        
        # Create tab bar for different config sections
        with dpg.tab_bar():
            # Audio tab
            with dpg.tab(label="Audio"):
                with dpg.group():
                    with dpg.group(horizontal=True):
                        dpg.add_text("Sample Rate:")
                        dpg.add_input_int(default_value=16000, min_value=8000, max_value=48000, step=1000)
                    
                    with dpg.group(horizontal=True):
                        dpg.add_text("Channels:")
                        dpg.add_input_int(default_value=1, min_value=1, max_value=2, step=1)
            
            # Whisper tab
            with dpg.tab(label="Whisper"):
                with dpg.group():
                    with dpg.group(horizontal=True):
                        dpg.add_text("Model Size:")
                        dpg.add_combo(items=["tiny", "base", "small", "medium", "large"], default_value="small")
                    
                    with dpg.group(horizontal=True):
                        dpg.add_text("Language:")
                        dpg.add_input_text(default_value="en")
            
            # Whisprd tab
            with dpg.tab(label="Whisprd"):
                with dpg.group():
                    with dpg.group(horizontal=True):
                        dpg.add_text("Confidence Threshold:")
                        dpg.add_slider_float(default_value=0.8, min_value=0.0, max_value=1.0)
                    
                    with dpg.group(horizontal=True):
                        dpg.add_text("Command Word:")
                        dpg.add_input_text(default_value="computer")
    
    def _on_start_clicked(self):
        """Handle start button click."""
        self.engine.start()
        self._update_button_states()
        dpg.configure_item(self.status_label, default_value="Engine ready")
    
    def _on_stop_clicked(self):
        """Handle stop button click."""
        self.engine.stop()
        self._update_button_states()
        dpg.configure_item(self.status_label, default_value="Engine stopped")
    
    def _on_toggle_clicked(self):
        """Handle toggle dictation button click."""
        if self.engine.is_dictating:
            self.engine.stop_dictation()
            dpg.configure_item(self.toggle_button, label="Start Dictation")
        else:
            self.engine.start_dictation()
            dpg.configure_item(self.toggle_button, label="Stop Dictation")
        self._update_button_states()
    
    def _on_pause_clicked(self):
        """Handle pause button click."""
        if self.engine.is_paused:
            self.engine.resume()
            dpg.configure_item(self.pause_button, label="Pause")
        else:
            self.engine.pause()
            dpg.configure_item(self.pause_button, label="Resume")
    
    def _update_button_states(self):
        """Update button states based on engine status."""
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
    
    def _on_clear_clicked(self):
        """Handle clear button click."""
        dpg.configure_item(self.current_text, default_value="")
        dpg.delete_item(self.history_group, children_only=True)
    
    def _on_save_clicked(self):
        """Handle save button click."""
        with dpg.window(label="Demo", modal=True, no_close=True, width=300, height=150):
            dpg.add_text("This is a demo - save functionality would work in the real app.")
            dpg.add_separator()
            dpg.add_button(label="OK", callback=lambda: dpg.delete_item(dpg.last_item_container()))
    
    def _on_reload_clicked(self):
        """Handle reload button click."""
        with dpg.window(label="Demo", modal=True, no_close=True, width=300, height=150):
            dpg.add_text("Configuration reloaded (demo mode).")
            dpg.add_separator()
            dpg.add_button(label="OK", callback=lambda: dpg.delete_item(dpg.last_item_container()))
    
    def _on_save_config_clicked(self):
        """Handle save config button click."""
        with dpg.window(label="Demo", modal=True, no_close=True, width=300, height=150):
            dpg.add_text("Configuration saved (demo mode).")
            dpg.add_separator()
            dpg.add_button(label="OK", callback=lambda: dpg.delete_item(dpg.last_item_container()))
    
    def _demo_loop(self):
        """Demo loop to simulate real-time updates."""
        demo_transcriptions = [
            "Hello, this is a demonstration of the whisprd GUI.",
            "The interface is built with DearPyGui for modern performance.",
            "You can see real-time status updates and transcription history.",
            "The configuration panel allows easy access to all settings.",
            "This demo shows the complete user interface without requiring the full engine."
        ]
        
        transcription_index = 0
        
        while True:
            time.sleep(3)  # Update every 3 seconds
            
            # Update status
            if self.engine.is_running:
                status = self.engine.get_status()
                
                # Update status indicators
                dpg.configure_item(self.status_engine, default_value="Running" if status['is_running'] else "Not running")
                dpg.configure_item(self.status_dictation, default_value="Active" if status['is_dictating'] else "Inactive")
                dpg.configure_item(self.status_audio_queue, default_value=str(status['audio_queue_size']))
                dpg.configure_item(self.status_transcription_queue, default_value=str(status['transcription_queue_size']))
                
                # Update statistics
                stats = status['stats']
                dpg.configure_item(self.stats_transcriptions, default_value=str(stats['total_transcriptions']))
                dpg.configure_item(self.stats_commands, default_value=str(stats['total_commands']))
                dpg.configure_item(self.stats_characters, default_value=str(stats['total_characters']))
                dpg.configure_item(self.stats_errors, default_value=str(stats['errors']))
                
                # Add demo transcription
                if self.engine.is_dictating and transcription_index < len(demo_transcriptions):
                    transcription = demo_transcriptions[transcription_index]
                    dpg.configure_item(self.current_text, default_value=transcription)
                    
                    # Add to history
                    with dpg.group(parent=self.history_group):
                        dpg.add_text(time.strftime("%H:%M:%S"))
                        dpg.add_text(transcription)
                        dpg.add_separator()
                    
                    transcription_index += 1
    
    def run(self):
        """Run the demo GUI."""
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()


def main():
    """Main entry point for the demo."""
    import argparse
    parser = argparse.ArgumentParser(description="Whisprd Demo GUI")
    parser.add_argument('--scale', type=float, help='Override UI scaling factor (e.g. 1.5)')
    parser.add_argument('--auto-scale-multiplier', type=float, default=1.1, help='Override auto scaling multiplier (default: 1.1)')
    args = parser.parse_args()
    print("🎤 Whisprd GUI Demo")
    print("This demonstrates the DearPyGui interface without requiring the full engine.")
    print("Press Ctrl+C to exit.")
    
    try:
        app = DemoGUI(scale=args.scale, auto_scale_multiplier=args.auto_scale_multiplier)
        app.run()
    except KeyboardInterrupt:
        print("\nDemo stopped by user.")
    except Exception as e:
        print(f"Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 