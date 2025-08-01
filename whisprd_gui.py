#!/usr/bin/env python3
"""
DearPyGui GUI for the whisprd system.
Provides a graphical interface for controlling and configuring whisprd.
"""

import sys
import signal
import argparse
import logging
import threading
import os
from pathlib import Path
from typing import Optional, Dict, Any, List

import dearpygui.dearpygui as dpg

from whisprd.dictation_engine import DictationEngine
from whisprd.gui.main_window import WhisprdMainWindow

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class WhisprdGUI:
    """Main GUI application for the whisprd system using DearPyGui."""
    
    def _detect_scaling(self, manual_scale: Optional[float] = None, auto_scale_multiplier: float = 1.1) -> float:
        """Detect system scaling factor or use manual override."""
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
    
    def __init__(self, config_path: Optional[str] = None, verbose: bool = False, scale: Optional[float] = None, auto_scale_multiplier: float = 1.1) -> None:
        """Initialize the GUI application."""
        self.config_path = config_path
        self.verbose = verbose
        
        # Set log level
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Detect and set scaling
        scale_factor = self._detect_scaling(scale, auto_scale_multiplier)
        dpg.create_context()
        dpg.set_global_font_scale(scale_factor)
        dpg.create_viewport(title="Whisprd - Real-time Dictation System", width=1200, height=800)
        dpg.setup_dearpygui()
        
        # Initialize dictation engine
        self.engine: Optional[DictationEngine] = None
        self.engine_thread: Optional[threading.Thread] = None
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Create main window
        self.main_window = WhisprdMainWindow(self)
        
        # Set main window as primary to fill viewport
        dpg.set_primary_window("main_window", True)
    
    def _signal_handler(self, signum: int, frame: Any) -> None:
        """Handle system signals."""
        logger.info("Received shutdown signal")
        self.stop_engine()
        dpg.stop_dearpygui()
    
    def _init_engine_async(self) -> None:
        """Initialize the dictation engine asynchronously."""
        def init_engine() -> None:
            try:
                self.engine = DictationEngine(self.config_path)
                
                # Set up callbacks
                self.engine.set_status_callback(self._on_status_change)
                self.engine.set_transcription_callback(self._on_transcription)
                
                # Update UI on main thread
                dpg.configure_item("status_indicator", default_value="✅ Ready")
                self.main_window.on_engine_ready(self.engine)
                
            except Exception as e:
                logger.error(f"Failed to initialize engine: {e}")
                dpg.configure_item("status_indicator", default_value="❌ Engine Error")
                self._show_error_dialog("Engine Initialization Failed", str(e))
        
        self.engine_thread = threading.Thread(target=init_engine, daemon=True)
        self.engine_thread.start()
    
    def _on_status_change(self, status: str) -> None:
        """Handle status changes from the engine."""
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
        
        self.main_window.update_status(status)
    
    def _on_transcription(self, original_text: str, clean_text: str, matches: List[Dict[str, Any]]) -> None:
        """Handle transcription results from the engine."""
        self.main_window.add_transcription(original_text, clean_text, matches)
    
    def start_engine(self) -> None:
        """Start the dictation engine."""
        if self.engine and not self.engine.is_running:
            try:
                self.engine.start()
                logger.info("Engine started")
            except Exception as e:
                logger.error(f"Failed to start engine: {e}")
                self._show_error_dialog("Failed to Start Engine", str(e))
    
    def stop_engine(self) -> None:
        """Stop the dictation engine."""
        if self.engine and self.engine.is_running:
            try:
                self.engine.stop()
                logger.info("Engine stopped")
            except Exception as e:
                logger.error(f"Error stopping engine: {e}")
    
    def _show_error_dialog(self, title: str, message: str) -> None:
        """Show an error dialog."""
        with dpg.window(label=title, modal=True, no_close=True, width=400, height=200):
            dpg.add_text(message)
            dpg.add_separator()
            dpg.add_button(label="OK", callback=lambda: dpg.delete_item(dpg.last_item_container()))
    
    def run(self) -> int:
        """Run the GUI application."""
        # Initialize engine in background
        self._init_engine_async()
        
        # Start DearPyGui
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()
        
        return 0


def main() -> int:
    """Main entry point for the GUI application."""
    parser = argparse.ArgumentParser(description="Whisprd GUI")
    parser.add_argument('--config', '-c', help='Path to configuration file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    parser.add_argument('--scale', type=float, help='Override UI scaling factor (e.g. 1.5)')
    parser.add_argument('--auto-scale-multiplier', type=float, default=1.1, help='Override autoscaling multiplier (default: 1.1)')
    
    args = parser.parse_args()
    
    # Create and run GUI application
    app = WhisprdGUI(args.config, args.verbose, args.scale, args.auto_scale_multiplier)
    return app.run()


if __name__ == "__main__":
    sys.exit(main()) 