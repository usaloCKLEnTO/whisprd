"""
Whisper transcription module using faster-whisper.
"""

import threading
import time
import queue
from typing import Dict, Any, Optional, Callable, List
import logging
import numpy as np

try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logging.warning("faster-whisper not available. Install with: pip install faster-whisper")

logger = logging.getLogger(__name__)


class WhisperTranscriber:
    """Whisper transcription using faster-whisper."""
    
    def __init__(self, config: Dict[str, Any], transcription_callback: Optional[Callable] = None):
        """
        Initialize Whisper transcriber.
        
        Args:
            config: Whisper configuration dictionary
            transcription_callback: Optional callback for transcription results
        """
        if not WHISPER_AVAILABLE:
            raise ImportError("faster-whisper is required but not installed")
        
        self.config = config
        self.transcription_callback = transcription_callback
        self.audio_queue: queue.Queue[bytes] = queue.Queue()
        self.is_running = False
        self.transcription_thread: Optional[threading.Thread] = None
        
        # Whisper settings
        self.model_size = config.get('model_size', 'small')
        self.language = config.get('language', 'en')
        self.beam_size = config.get('beam_size', 5)
        self.best_of = config.get('best_of', 5)
        self.temperature = config.get('temperature', 0.0)
        self.condition_on_previous_text = config.get('condition_on_previous_text', True)
        self.initial_prompt = config.get('initial_prompt', '')
        
        # Initialize model
        self.model = None
        self._load_model()
        
        logger.info(f"Whisper transcriber initialized with model: {self.model_size}")
    
    def _load_model(self) -> None:
        """Load Whisper model."""
        try:
            logger.info(f"Loading Whisper model: {self.model_size}")
            self.model = WhisperModel(
                self.model_size,
                device="cpu",  # Force CPU to avoid CUDA issues
                compute_type="int8"  # Use int8 for CPU
            )
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    def start_transcription(self) -> None:
        """Start transcription thread."""
        if self.is_running:
            logger.warning("Transcription already running")
            return
        
        self.is_running = True
        self.transcription_thread = threading.Thread(target=self._transcription_loop, daemon=True)
        self.transcription_thread.start()
        logger.info("Transcription thread started")
    
    def stop_transcription(self) -> None:
        """Stop transcription thread."""
        if not self.is_running:
            logger.warning("Transcription not running")
            return
        
        self.is_running = False
        if self.transcription_thread:
            self.transcription_thread.join(timeout=5.0)
        logger.info("Transcription thread stopped")
    
    def _transcription_loop(self) -> None:
        """Main transcription loop with silence-based utterance segmentation and robust deduplication."""
        buffer = b""
        last_transcription = ""
        silence_buffer = b""
        
        # Get pause duration settings from config
        silence_duration = self.config.get('pause_duration', 1.0)  # seconds of silence to trigger utterance boundary
        min_utterance_duration = self.config.get('min_utterance_duration', 0.7)  # minimum utterance length to transcribe
        overlap_duration = self.config.get('overlap_duration', 0.2)  # seconds to keep as overlap
        
        sample_rate = 16000  # default, can be made configurable
        bytes_per_sample = 2  # int16
        chunk_size = int(sample_rate * bytes_per_sample * 0.1)  # 100ms chunks
        
        while self.is_running:
            try:
                # Get next chunk (100ms)
                audio_data = self.audio_queue.get(timeout=1.0)
                buffer += audio_data
                
                # Always keep a rolling silence buffer (last silence_duration seconds)
                silence_buffer += audio_data
                if len(silence_buffer) > int(sample_rate * bytes_per_sample * silence_duration):
                    silence_buffer = silence_buffer[-int(sample_rate * bytes_per_sample * silence_duration):]
                
                # Check for silence at the end of buffer
                audio_array = np.frombuffer(silence_buffer, dtype=np.int16).astype(np.float32) / 32768.0
                if self._is_silence(audio_array, threshold=0.01):
                    # Only process if utterance is long enough
                    if len(buffer) > int(sample_rate * bytes_per_sample * min_utterance_duration):
                        # Remove trailing silence from utterance
                        utterance = buffer[:-len(silence_buffer)] if len(buffer) > len(silence_buffer) else buffer
                        if len(utterance) > 0:
                            result = self._transcribe_audio(utterance)
                            if result and result.strip():
                                # Deduplication/correction logic
                                if self._is_new_content(result.strip(), last_transcription):
                                    self._process_transcription(result.strip())
                                    last_transcription = result.strip()
                                elif result.strip() != last_transcription and len(result.strip()) > len(last_transcription):
                                    # Correction/superset: replace previous output
                                    self._process_transcription(result.strip())
                                    last_transcription = result.strip()
                        # Keep overlap for next buffer
                        buffer = buffer[-int(sample_rate * bytes_per_sample * overlap_duration):]
                    else:
                        # Too short, just clear buffer
                        buffer = b""
                    silence_buffer = b""
                # If buffer grows too large (e.g., >10s), force flush
                if len(buffer) > int(sample_rate * bytes_per_sample * 10):
                    result = self._transcribe_audio(buffer)
                    if result and result.strip():
                        if self._is_new_content(result.strip(), last_transcription):
                            self._process_transcription(result.strip())
                            last_transcription = result.strip()
                    buffer = b""
                    silence_buffer = b""
            except queue.Empty:
                # On timeout, flush any remaining utterance if not silence
                if buffer and len(buffer) > int(sample_rate * bytes_per_sample * min_utterance_duration):
                    result = self._transcribe_audio(buffer)
                    if result and result.strip():
                        if self._is_new_content(result.strip(), last_transcription):
                            self._process_transcription(result.strip())
                            last_transcription = result.strip()
                buffer = b""
                silence_buffer = b""
                continue
            except Exception as e:
                logger.error(f"Error in transcription loop: {e}")
                time.sleep(0.1)
    
    def _is_new_content(self, new_text: str, last_text: str) -> bool:
        """
        Check if new text contains significant new content.
        
        Args:
            new_text: New transcription text
            last_text: Previous transcription text
            
        Returns:
            True if new content is significant
        """
        if not last_text:
            return True
        
        # Normalize text for comparison
        new_text_norm = new_text.lower().strip()
        last_text_norm = last_text.lower().strip()
        
        # If texts are identical, it's not new content
        if new_text_norm == last_text_norm:
            return False
        
        # Check if new text is contained within the last text (common with overlapping audio)
        if new_text_norm in last_text_norm:
            return False
        
        # Check if last text is contained within new text (expansion case)
        if last_text_norm in new_text_norm:
            # Only consider it new if it's significantly longer
            if len(new_text_norm) > len(last_text_norm) * 1.3:
                return True
            return False
        
        # Check for significant overlap at the beginning or end
        new_words = new_text_norm.split()
        last_words = last_text_norm.split()
        
        if len(new_words) > 0 and len(last_words) > 0:
            # Check for overlap at the beginning
            overlap_start = 0
            for i in range(min(len(new_words), len(last_words))):
                if new_words[i] == last_words[i]:
                    overlap_start += 1
                else:
                    break
            
            # If more than 50% of words overlap at the start, it's likely a duplicate
            if overlap_start > len(new_words) * 0.5:
                return False
            
            # Check for overlap at the end
            overlap_end = 0
            for i in range(min(len(new_words), len(last_words))):
                if new_words[-(i+1)] == last_words[-(i+1)]:
                    overlap_end += 1
                else:
                    break
            
            # If more than 50% of words overlap at the end, it's likely a duplicate
            if overlap_end > len(new_words) * 0.5:
                return False
        
        # Check for new unique words
        new_word_set = set(new_words)
        last_word_set = set(last_words)
        new_unique_words = new_word_set - last_word_set
        
        # If there are significant new words, it's new content
        if len(new_unique_words) >= 2:
            return True
        
        # If new text is significantly longer, it's new content
        if len(new_text_norm) > len(last_text_norm) * 1.5:
            return True
        
        # If the text is completely different, it's new content
        if new_text_norm != last_text_norm:
            # But only if it's not just a minor variation
            if len(new_text_norm) > 3 and len(last_text_norm) > 3:
                return True
        
        return False
    
    def _transcribe_audio(self, audio_data: bytes) -> Optional[str]:
        """
        Transcribe audio data using Whisper.
        
        Args:
            audio_data: Raw audio data as bytes
            
        Returns:
            Transcribed text or None if failed
        """
        try:
            # Convert bytes to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            
            # Check for silence - if audio is mostly silence, don't transcribe
            if self._is_silence(audio_array):
                return None
            
            if self.model is None:
                logger.error("Whisper model is not loaded.")
                return None
            # Transcribe with Whisper
            segments, info = self.model.transcribe(
                audio_array,
                language=self.language,
                beam_size=self.beam_size,
                best_of=self.best_of,
                temperature=self.temperature,
                condition_on_previous_text=self.condition_on_previous_text,
                initial_prompt=self.initial_prompt if self.initial_prompt else None
            )
            # Combine segments
            text = " ".join([segment.text for segment in segments])
            return text.strip()
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return None
    
    def _is_silence(self, audio_array: np.ndarray, threshold: float = 0.01) -> bool:
        """
        Check if audio is mostly silence.
        
        Args:
            audio_array: Audio data as numpy array
            threshold: RMS threshold for silence detection
            
        Returns:
            True if audio is mostly silence
        """
        if audio_array.size == 0:
            return True
        rms = np.sqrt(np.mean(audio_array**2))
        return bool(rms < threshold)
    
    def _process_transcription(self, text: str) -> None:
        """Process transcription result."""
        logger.debug(f"Transcription: {text}")
        
        if self.transcription_callback:
            try:
                self.transcription_callback(text)
            except Exception as e:
                logger.error(f"Error in transcription callback: {e}")
    
    def add_audio_data(self, audio_data: bytes) -> None:
        """
        Add audio data to transcription queue.
        
        Args:
            audio_data: Raw audio data as bytes
        """
        if not self.is_running:
            logger.warning("Transcription not running, cannot add audio data")
            return
        
        try:
            self.audio_queue.put(audio_data, timeout=0.1)
        except queue.Full:
            logger.warning("Audio queue full, dropping audio data")
    
    def get_queue_size(self) -> int:
        """Get current audio queue size."""
        return self.audio_queue.qsize()
    
    def clear_queue(self) -> None:
        """Clear the audio queue."""
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
    
    def transcribe_file(self, file_path: str) -> Optional[str]:
        """
        Transcribe an audio file.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Transcribed text or None if failed
        """
        try:
            if self.model is None:
                logger.error("Whisper model is not loaded.")
                return None
            segments, info = self.model.transcribe(
                file_path,
                language=self.language,
                beam_size=self.beam_size,
                best_of=self.best_of,
                temperature=self.temperature
            )
            text = " ".join([segment.text for segment in segments])
            return text.strip()
        except Exception as e:
            logger.error(f"File transcription error: {e}")
            return None
    
    def __enter__(self) -> 'WhisperTranscriber':
        """Context manager entry."""
        self.start_transcription()
        return self
    
    def __exit__(self, exc_type: Optional[type], exc_val: Optional[BaseException], exc_tb: Optional[object]) -> None:
        """Context manager exit."""
        self.stop_transcription() 