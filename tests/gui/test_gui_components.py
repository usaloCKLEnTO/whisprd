"""
GUI tests for whisprd GUI components.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any


class TestGUIComponents:
    """Test cases for GUI components."""

    def test_gui_imports(self) -> None:
        """Test that GUI modules can be imported."""
        # This test ensures that the GUI modules can be imported
        # even when DearPyGui is not available
        try:
            with patch.dict('sys.modules', {'dearpygui': Mock()}):
                import whisprd.gui.main_window
                import whisprd.gui.control_panel
                import whisprd.gui.status_panel
                import whisprd.gui.transcription_panel
                import whisprd.gui.config_panel
        except ImportError:
            pytest.skip("GUI modules not available")

    def test_gui_config_loading(self, sample_config: Dict[str, Any]) -> None:
        """Test GUI configuration loading."""
        # Test that GUI components can handle configuration
        with patch.dict('sys.modules', {'dearpygui': Mock()}):
            try:
                from whisprd.gui.main_window import MainWindow
                
                with patch('whisprd.gui.main_window.dearpygui') as mock_dpg:
                    window = MainWindow(sample_config)
                    assert window.config == sample_config
            except ImportError:
                pytest.skip("GUI modules not available")

    def test_gui_callbacks(self, sample_config: Dict[str, Any]) -> None:
        """Test GUI callback functionality."""
        with patch.dict('sys.modules', {'dearpygui': Mock()}):
            try:
                from whisprd.gui.main_window import MainWindow
                
                with patch('whisprd.gui.main_window.dearpygui') as mock_dpg:
                    window = MainWindow(sample_config)
                    
                    # Test setting callbacks
                    start_callback = Mock()
                    stop_callback = Mock()
                    pause_callback = Mock()
                    clear_callback = Mock()
                    
                    window.set_callbacks(start_callback, stop_callback, pause_callback, clear_callback)
                    
                    assert window.start_callback == start_callback
                    assert window.stop_callback == stop_callback
                    assert window.pause_callback == pause_callback
                    assert window.clear_callback == clear_callback
            except ImportError:
                pytest.skip("GUI modules not available")

    def test_gui_status_updates(self, sample_config: Dict[str, Any]) -> None:
        """Test GUI status update functionality."""
        with patch.dict('sys.modules', {'dearpygui': Mock()}):
            try:
                from whisprd.gui.status_panel import StatusPanel
                
                with patch('whisprd.gui.status_panel.dearpygui') as mock_dpg:
                    panel = StatusPanel(sample_config)
                    
                    # Test status updates
                    panel.update_status("Running", "green")
                    mock_dpg.set_value.assert_called()
            except ImportError:
                pytest.skip("GUI modules not available")

    def test_gui_transcript_updates(self, sample_config: Dict[str, Any]) -> None:
        """Test GUI transcript update functionality."""
        with patch.dict('sys.modules', {'dearpygui': Mock()}):
            try:
                from whisprd.gui.transcription_panel import TranscriptionPanel
                
                with patch('whisprd.gui.transcription_panel.dearpygui') as mock_dpg:
                    panel = TranscriptionPanel(sample_config)
                    
                    # Test transcript updates
                    panel.update_transcript("Test transcript")
                    mock_dpg.set_value.assert_called()
            except ImportError:
                pytest.skip("GUI modules not available") 