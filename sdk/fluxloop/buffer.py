"""
Event buffering and batch sending logic.
"""

import atexit
import json
import threading
import time
from collections import deque
from datetime import datetime
from typing import Any, Deque, Dict, List, Optional, Tuple
from uuid import UUID

from .config import get_config
from .models import ObservationData, TraceData
from .storage import OfflineStore


class EventBuffer:
    """
    Singleton buffer for collecting and batching events.
    """
    
    _instance: Optional["EventBuffer"] = None
    _lock = threading.Lock()
    
    def __init__(self):
        """Initialize the buffer."""
        if EventBuffer._instance is not None:
            raise RuntimeError("Use EventBuffer.get_instance() instead")
        
        self.config = get_config()
        self.traces: Deque[TraceData] = deque(maxlen=self.config.max_queue_size)
        self.observations: Deque[Tuple[UUID, ObservationData]] = deque(
            maxlen=self.config.max_queue_size
        )
        
        # Threading
        self.send_lock = threading.Lock()
        self.last_flush = time.time()
        
        # Background thread for periodic flushing
        self.stop_event = threading.Event()
        self.flush_thread = threading.Thread(target=self._flush_periodically, daemon=True)
        self.flush_thread.start()
        
        # Register cleanup on exit
        atexit.register(self.shutdown)

        # Offline store
        self.offline_store = OfflineStore()
    
    @classmethod
    def get_instance(cls) -> "EventBuffer":
        """Get or create the singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    def add_trace(self, trace: TraceData) -> None:
        """
        Add a trace to the buffer.
        
        Args:
            trace: Trace data to add
        """
        if not self.config.enabled:
            return
        
        with self.send_lock:
            self.traces.append(trace)
    
    def add_observation(self, trace_id: UUID, observation: ObservationData) -> None:
        """
        Add an observation to the buffer.
        
        Args:
            trace_id: ID of the parent trace
            observation: Observation data to add
        """
        if not self.config.enabled:
            return
        
        with self.send_lock:
            self.observations.append((trace_id, observation))
    
    def flush_if_needed(self) -> None:
        """Flush the buffer if batch size is reached."""
        should_flush = False
        
        with self.send_lock:
            total_items = len(self.traces) + len(self.observations)
            should_flush = total_items >= self.config.batch_size
        
        if should_flush:
            self.flush()
    
    def flush(self) -> None:
        """Send all buffered events to the collector."""
        if not self.config.enabled:
            return
        
        # Collect items to send
        traces_to_send: List[TraceData] = []
        observations_to_send: List[Tuple[UUID, ObservationData]] = []
        
        with self.send_lock:
            # Move items from buffer
            while self.traces:
                traces_to_send.append(self.traces.popleft())
            
            while self.observations:
                observations_to_send.append(self.observations.popleft())
            
            self.last_flush = time.time()
        
        # Send if there's data
        if traces_to_send or observations_to_send:
            self._send_batch(traces_to_send, observations_to_send)
    
    def _send_batch(
        self,
        traces: List[TraceData],
        observations: List[Tuple[UUID, ObservationData]]
    ) -> None:
        """
        Send a batch of events to the collector.
        
        Args:
            traces: List of traces to send
            observations: List of (trace_id, observation) tuples
        """
        # Import here to avoid circular dependency
        send_errors = False

        if self.config.use_collector:
            from .client import FluxLoopClient

            client = FluxLoopClient()

            for trace in traces:
                try:
                    client.send_trace(trace)
                except Exception as e:
                    send_errors = True
                    if self.config.debug:
                        print(f"Failed to send trace {trace.id}: {e}")

            for trace_id, observation in observations:
                try:
                    client.send_observation(trace_id, observation)
                except Exception as e:
                    send_errors = True
                    if self.config.debug:
                        print(f"Failed to send observation {observation.id}: {e}")

        if send_errors or not self.config.use_collector:
            self.offline_store.record_traces(traces)
            self.offline_store.record_observations(observations)
    
    def _flush_periodically(self) -> None:
        """Background thread to flush periodically."""
        while not self.stop_event.is_set():
            time.sleep(self.config.flush_interval)
            
            # Check if enough time has passed since last flush
            with self.send_lock:
                time_since_flush = time.time() - self.last_flush
                has_data = bool(self.traces or self.observations)
            
            if has_data and time_since_flush >= self.config.flush_interval:
                self.flush()
    
    def shutdown(self) -> None:
        """Shutdown the buffer and flush remaining events."""
        # Stop the background thread
        self.stop_event.set()
        
        # Final flush
        self.flush()
        
        # Wait for thread to stop (with timeout)
        if self.flush_thread.is_alive():
            self.flush_thread.join(timeout=2.0)
