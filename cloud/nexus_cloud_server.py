# ============================================================
# NEXUS CLOUD SERVER (24/7 AUTONOMOUS WEB SERVICE)
# Standard library HTTP Server + Threading for zero-friction deploy
# ============================================================

import os
import sys
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse, parse_qs

# Ensure root workspace is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from cloud.autopilot import cloud_autopilot
from cloud.remote_bot import remote_bot

logger = logging.getLogger("NexusCloudServer")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handles each incoming request in a new thread."""
    daemon_threads = True


class NexusCloudHandler(BaseHTTPRequestHandler):
    """
    REST API Handler for NEXUS 24/7 Cloud Engine.
    Provides health checks, draft generation, approvals, and desktop sync.
    """

    def _send_json(self, status_code: int, data: dict):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/", "/health"):
            sync = cloud_autopilot.get_sync_payload()
            self._send_json(200, {
                "service": "NEXUS V1 24/7 Cloud Autonomous Node",
                "status": "ONLINE",
                "niche": sync.get("niche"),
                "pending_drafts": sync.get("pending_count"),
                "approved_drafts": sync.get("approved_count"),
            })
            return

        if path == "/api/status":
            self._send_json(200, cloud_autopilot.get_sync_payload())
            return

        if path == "/api/sync":
            # Sync endpoint queried by Desktop NEXUS when laptop wakes up
            self._send_json(200, cloud_autopilot.get_sync_payload())
            return

        if path == "/api/queue":
            self._send_json(200, {
                "pending_drafts": cloud_autopilot.state.get("pending_drafts", []),
                "approved_drafts": cloud_autopilot.state.get("approved_drafts", []),
            })
            return

        self._send_json(404, {"error": "Endpoint not found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        try:
            payload = json.loads(body) if body else {}
        except Exception:
            payload = {}

        if path == "/api/generate_draft":
            topic = payload.get("topic")
            draft = cloud_autopilot.generate_autonomous_draft(topic)
            self._send_json(200, {
                "status": "SUCCESS",
                "draft": draft,
            })
            return

        if path == "/api/approve":
            draft_id = payload.get("draft_id")
            if not draft_id:
                self._send_json(400, {"error": "Missing 'draft_id' in payload"})
                return

            success = cloud_autopilot.approve_draft(draft_id)
            if success:
                self._send_json(200, {"status": "APPROVED", "draft_id": draft_id})
            else:
                self._send_json(404, {"error": "Draft not found or already processed"})
            return

        if path == "/api/reject":
            draft_id = payload.get("draft_id")
            if not draft_id:
                self._send_json(400, {"error": "Missing 'draft_id' in payload"})
                return

            success = cloud_autopilot.reject_draft(draft_id)
            if success:
                self._send_json(200, {"status": "REJECTED", "draft_id": draft_id})
            else:
                self._send_json(404, {"error": "Draft not found"})
            return

        if path == "/api/set_niche":
            niche = payload.get("niche")
            if niche:
                cloud_autopilot.state["niche"] = niche
                cloud_autopilot._save_storage()
                self._send_json(200, {"status": "SUCCESS", "niche": niche})
            else:
                self._send_json(400, {"error": "Missing 'niche' parameter"})
            return

        self._send_json(404, {"error": "Endpoint not found"})


_server_thread = None
_running_server = None


def run_cloud_server(host: str = "0.0.0.0", port: int = None):
    """Start the 24/7 Cloud Server and its background workers."""
    global _running_server
    if port is None:
        port = int(os.getenv("PORT", os.getenv("NEXUS_CLOUD_PORT", "8000")))

    # Start 24/7 Autopilot Loop
    cloud_autopilot.start()

    # Start Telegram Remote Bot if configured
    remote_bot.start()

    try:
        server = ThreadedHTTPServer((host, port), NexusCloudHandler)
        _running_server = server
        logger.info("==================================================")
        logger.info(f"NEXUS 24/7 CLOUD SERVER ONLINE at http://{host}:{port}")
        logger.info(f"Health check endpoint: http://{host}:{port}/health")
        logger.info(f"Desktop sync endpoint: http://{host}:{port}/api/sync")
        logger.info("==================================================")
        server.serve_forever()
    except OSError as e:
        logger.warning(f"Port {port} already bound or in use ({e}). Server is likely already running.")
    except KeyboardInterrupt:
        logger.info("Shutting down NEXUS Cloud Server...")
    finally:
        cloud_autopilot.stop()
        remote_bot.stop()
        if _running_server:
            try:
                _running_server.server_close()
            except Exception:
                pass
            _running_server = None


def start_cloud_server_background(host: str = "0.0.0.0", port: int = 8000) -> bool:
    """Start cloud server as a non-blocking background daemon thread."""
    global _server_thread
    from cloud.sync_client import cloud_sync
    if cloud_sync.check_connection():
        return True

    def _worker():
        run_cloud_server(host, port)

    _server_thread = threading.Thread(target=_worker, daemon=True, name="NexusCloudServerThread")
    _server_thread.start()

    # Wait up to 3 seconds for server to start listening
    for _ in range(6):
        time.sleep(0.5)
        if cloud_sync.check_connection():
            return True

    return cloud_sync.check_connection()


def stop_cloud_server():
    """Stop the running background cloud server."""
    global _running_server
    if _running_server:
        try:
            _running_server.shutdown()
        except Exception:
            pass


if __name__ == "__main__":
    run_cloud_server()
