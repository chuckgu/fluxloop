"""
HTTP client for sending data to the collector.
"""

import json
from typing import Any, Dict, Optional
from uuid import UUID

import httpx

from .config import get_config
from .models import ObservationData, TraceData


class FluxLoopClient:
    """
    HTTP client for communicating with the FluxLoop collector.
    """
    
    def __init__(self, collector_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize the client.
        
        Args:
            collector_url: Override collector URL
            api_key: Override API key
        """
        self.config = get_config()
        self.collector_url = collector_url or self.config.collector_url
        self.api_key = api_key or self.config.api_key
        self._client: Optional[httpx.Client] = None
        if self.config.use_collector:
            self._client = httpx.Client(
                base_url=self.collector_url,
                timeout=self.config.timeout,
                headers=self._get_headers(),
            )
    
    def _get_headers(self) -> Dict[str, str]:
        """Get common headers for requests."""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "fluxloop-sdk/0.1.0",
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        if self.config.service_name:
            headers["X-Service-Name"] = self.config.service_name
        
        if self.config.environment:
            headers["X-Environment"] = self.config.environment
        
        return headers
    
    def send_trace(self, trace: TraceData) -> Dict[str, Any]:
        """
        Send a trace to the collector.
        
        Args:
            trace: Trace data to send
            
        Returns:
            Response from the collector
            
        Raises:
            httpx.HTTPError: If the request fails
        """
        if not self.config.enabled:
            return {"status": "disabled"}
        
        # Convert to JSON-serializable format
        payload = self._serialize_trace(trace)
        
        if not self._client:
            return {"status": "collector_disabled"}
        
        try:
            response = self._client.post("/api/traces", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            if self.config.debug:
                print(f"Error sending trace: {e}")
            raise
    
    def send_observation(
        self, trace_id: UUID, observation: ObservationData
    ) -> Dict[str, Any]:
        """
        Send an observation to the collector.
        
        Args:
            trace_id: ID of the parent trace
            observation: Observation data to send
            
        Returns:
            Response from the collector
            
        Raises:
            httpx.HTTPError: If the request fails
        """
        if not self.config.enabled:
            return {"status": "disabled"}
        
        # Convert to JSON-serializable format
        payload = self._serialize_observation(observation)
        payload["trace_id"] = str(trace_id)
        
        if not self._client:
            return {"status": "collector_disabled"}
        
        try:
            response = self._client.post(
                f"/api/traces/{trace_id}/observations",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            if self.config.debug:
                print(f"Error sending observation: {e}")
            raise
    
    def _serialize_trace(self, trace: TraceData) -> Dict[str, Any]:
        """Serialize trace for JSON transmission."""
        data = trace.model_dump(exclude_none=True)
        
        # Convert UUIDs to strings
        if "id" in data:
            data["id"] = str(data["id"])
        if "session_id" in data:
            data["session_id"] = str(data["session_id"])
        
        # Convert datetime to ISO format
        if "start_time" in data:
            data["start_time"] = data["start_time"].isoformat()
        if "end_time" in data and data["end_time"]:
            data["end_time"] = data["end_time"].isoformat()
        
        return data
    
    def _serialize_observation(self, observation: ObservationData) -> Dict[str, Any]:
        """Serialize observation for JSON transmission."""
        data = observation.model_dump(exclude_none=True)
        
        # Convert UUIDs to strings
        if "id" in data:
            data["id"] = str(data["id"])
        if "parent_observation_id" in data:
            data["parent_observation_id"] = str(data["parent_observation_id"])
        if "trace_id" in data:
            data["trace_id"] = str(data["trace_id"])
        
        # Convert datetime to ISO format
        if "start_time" in data:
            data["start_time"] = data["start_time"].isoformat()
        if "end_time" in data and data["end_time"]:
            data["end_time"] = data["end_time"].isoformat()
        
        return data
    
    def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            self._client.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
