"""HTTP health check server for deployment monitoring."""

import asyncio
import json
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from typing import Dict, Any

logger = logging.getLogger(__name__)


class HealthCheckHandler(BaseHTTPRequestHandler):
    """HTTP handler for health check endpoints."""
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == "/health":
            self._handle_health_check()
        elif self.path == "/ready":
            self._handle_readiness_check()
        else:
            self._handle_not_found()
    
    def _handle_health_check(self):
        """Handle basic health check."""
        response = {
            "status": "healthy",
            "timestamp": asyncio.get_event_loop().time() if asyncio._get_running_loop() else 0,
            "service": "vinbot-decoder"
        }
        self._send_json_response(200, response)
    
    def _handle_readiness_check(self):
        """Handle readiness check."""
        # For now, just check if we can respond
        # TODO: Add actual service dependency checks
        response = {
            "status": "ready",
            "timestamp": asyncio.get_event_loop().time() if asyncio._get_running_loop() else 0,
            "dependencies": {
                "telegram_api": "unknown",
                "external_services": "unknown"
            }
        }
        self._send_json_response(200, response)
    
    def _handle_not_found(self):
        """Handle 404 responses."""
        response = {"error": "Not found"}
        self._send_json_response(404, response)
    
    def _send_json_response(self, status_code: int, data: Dict[str, Any]):
        """Send JSON response."""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def log_message(self, format, *args):
        """Override to use our logger."""
        logger.info(f"Health check: {format % args}")


class HealthCheckServer:
    """HTTP server for health checks."""
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.server = None
        self.thread = None
    
    def start(self):
        """Start the health check server in a separate thread."""
        try:
            self.server = HTTPServer(('0.0.0.0', self.port), HealthCheckHandler)
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            logger.info(f"Health check server started on port {self.port}")
        except Exception as e:
            logger.error(f"Failed to start health check server: {e}")
    
    def stop(self):
        """Stop the health check server."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            logger.info("Health check server stopped")
        if self.thread:
            self.thread.join(timeout=5)
