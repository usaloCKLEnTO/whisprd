"""
Real-time audio capture module for the dictation system.
"""

import queue
import threading
import time
import numpy as np
import sounddevice as sd
from typing import Callable, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class AudioCapture:
    """Real-time audio capture using sounddevice."""
    
    def __init__(self, config: Dict[str, Any], audio_callback: Optional[Callable] = None):
        """
        Initialize audio capture.
        
        Args:
            config: Audio configuration dictionary
            audio_callback: Optional callback function for audio data
        """
        self.config = config
        self.audio_callback = audio_callback
        self.audio_queue = queue.Queue()
        self.stream = None
        self.is_recording = False
        self.recording_thread = None
        
        # Audio settings
        self.sample_rate = config.get('sample_rate', 16000)
        self.channels = config.get('channels', 1)
        self.buffer_size = config.get('buffer_size', 8000)
        self.device = config.get('device')
        
        logger.info(f"Audio capture initialized: {self.sample_rate}Hz, {self.channels}ch, buffer={self.buffer_size}")
    
    def _audio_callback(self, indata, frames, time, status):
        """Internal audio callback for sounddevice."""
        if status:
            logger.warning(f"Audio callback status: {status}")
        
        # Convert to bytes and add to queue
        audio_data = bytes(indata)
        self.audio_queue.put(audio_data)
        
        # Call external callback if provided
        if self.audio_callback:
            try:
                self.audio_callback(audio_data, time)
            except Exception as e:
                logger.error(f"Error in audio callback: {e}")
    
    def start_recording(self):
        """Start audio recording."""
        if self.is_recording:
            logger.warning("Audio recording already started")
            return
        
        try:
            # Create audio stream
            self.stream = sd.RawInputStream(
                callback=self._audio_callback,
                samplerate=self.sample_rate,
                channels=self.channels,
                blocksize=self.buffer_size,
                dtype=np.int16,
                device=self.device
            )
            
            self.stream.start()
            self.is_recording = True
            
            logger.info("Audio recording started")
            
        except Exception as e:
            logger.error(f"Failed to start audio recording: {e}")
            raise
    
    def stop_recording(self):
        """Stop audio recording."""
        if not self.is_recording:
            logger.warning("Audio recording not started")
            return
        
        try:
            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None
            
            self.is_recording = False
            logger.info("Audio recording stopped")
            
        except Exception as e:
            logger.error(f"Error stopping audio recording: {e}")
    
    def get_audio_data(self, timeout: float = 1.0) -> Optional[bytes]:
        """
        Get audio data from the queue.
        
        Args:
            timeout: Timeout in seconds for getting data
            
        Returns:
            Audio data as bytes or None if timeout
        """
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def get_audio_buffer(self, duration_seconds: float = 1.0) -> Optional[bytes]:
        """
        Get audio buffer of specified duration.
        
        Args:
            duration_seconds: Duration of audio buffer in seconds
            
        Returns:
            Audio data as bytes or None if not enough data
        """
        target_size = int(self.sample_rate * self.channels * 2 * duration_seconds)  # 2 bytes per sample
        buffer = b""
        
        start_time = time.time()
        while len(buffer) < target_size:
            data = self.get_audio_data(timeout=0.1)
            if data is None:
                if time.time() - start_time > 5.0:  # 5 second timeout
                    return None
                continue
            
            buffer += data
        
        return buffer
    
    def get_queue_size(self) -> int:
        """Get current audio queue size."""
        return self.audio_queue.qsize()
    
    def clear_queue(self):
        """Clear the audio queue."""
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
    
    def list_devices(self) -> list:
        """List available audio devices."""
        try:
            devices = sd.query_devices()
            return devices
        except Exception as e:
            logger.error(f"Error listing audio devices: {e}")
            return []
    
    def get_default_device(self) -> Optional[int]:
        """Get default input device."""
        try:
            return sd.default.device[0]  # Input device
        except Exception as e:
            logger.error(f"Error getting default device: {e}")
            return None
    
    def __enter__(self):
        """Context manager entry."""
        self.start_recording()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_recording() 