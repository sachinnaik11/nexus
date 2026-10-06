# ============================================================
# NEXUS PRIVATE AI BRAIN SERVER (PC & PHONE ACCESSIBLE)
# Dual Engine: NVIDIA RTX 4050 Local Thinking + Gemini Creation
# ============================================================

import os
import sys
import json
import re
import socket
import logging
import secrets
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)

logger = logging.getLogger("NexusAIServer")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

PIN = os.getenv("AI_PIN", "2026").strip()
VALID_TOKENS = set()
HISTORY_FILE = os.path.join(BASE_DIR, "data", "private_ai_history.json")


def get_local_ip() -> str:
    """Detect LAN IPv4 address for phone browser access."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def query_ollama_local(prompt: str) -> dict:
    """Query local Qwen3 8B running on NVIDIA RTX 4050 GPU with thinking extraction."""
    url = "http://127.0.0.1:11434/api/generate"
    payload = {
        "model": "qwen3:8b",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": 1024
        }
    }
    try:
        res = requests.post(url, json=payload, timeout=120)
        if res.status_code == 200:
            data = res.json()
            raw = data.get("response", "")
            thinking = data.get("thinking", "")
            if not thinking:
                think_match = re.search(r"<think>(.*?)</think>", raw, re.DOTALL)
                if think_match:
                    thinking = think_match.group(1).strip()
                    clean_text = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()
                else:
                    clean_text = raw
            else:
                clean_text = raw

            if not clean_text and thinking:
                clean_text = thinking.split("\n\n")[-1].strip() if "\n\n" in thinking else thinking

            return {"success": True, "response": clean_text, "thinking": thinking, "engine": "RTX 4050 (Qwen3)"}
        return {"success": False, "message": f"Ollama HTTP {res.status_code}: {res.text[:200]}"}
    except Exception as e:
        return {"success": False, "message": f"Local Ollama error (check if Ollama is running): {e}"}


def query_gemini_cloud(prompt: str) -> dict:
    """Query Google Gemini with deep reasoning instructions."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return {"success": False, "message": "Missing GEMINI_API_KEY in .env"}

    system_prompt = (
        "You are NEXUS Brain, a personal super-intelligence assisting your owner across their PC and mobile phone.\n"
        "Provide thorough, high-IQ reasoning, creative concepts, and precise execution.\n"
        "Format your internal thoughts first inside <think>...</think> tags, followed by your final answer."
    )

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        chat = client.chats.create(model="gemini-3.5-flash-lite")
        full_query = f"{system_prompt}\n\nUser Request: {prompt}"
        res = chat.send_message(full_query)
        raw = res.text.strip()

        thinking = ""
        think_match = re.search(r"<think>(.*?)</think>", raw, re.DOTALL)
        if think_match:
            thinking = think_match.group(1).strip()
            clean_text = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()
        else:
            clean_text = raw

        return {"success": True, "response": clean_text, "thinking": thinking, "engine": "Cloud Gemini 3.5"}
    except Exception as e:
        return {"success": False, "message": f"Gemini Cloud error: {e}"}


class ThreadedServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


def get_active_tunnel_url() -> str:
    """Retrieve the active Cloudflare tunnel URL."""
    t_file = os.path.join(BASE_DIR, "data", "tunnel_url.txt")
    if os.path.exists(t_file):
        with open(t_file, "r", encoding="utf-8") as f:
            u = f.read().strip()
            if u.startswith("https://") and "trycloudflare.com" in u:
                return u
    log_file = os.path.join(BASE_DIR, "data", "tunnel.log")
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
                if match:
                    u = match.group(0)
                    with open(t_file, "w", encoding="utf-8") as out:
                        out.write(u)
                    return u
    return "https://ivory-stuart-paso-implied.trycloudflare.com"


def update_qr_code(url: str):
    """Generate high-contrast QR code PNG for easy phone scanning."""
    try:
        import qrcode
        qr = qrcode.QRCode(box_size=8, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(os.path.join(BASE_DIR, "web", "phone_qr.png"))
    except Exception as e:
        logger.warning(f"QR generation skipped: {e}")


def ensure_cloudflared_running(port: int = 5050):
    """Ensure Cloudflare tunnel background daemon is active."""
    import subprocess
    try:
        out = subprocess.check_output("tasklist /FI \"IMAGENAME eq cloudflared.exe\"", shell=True).decode()
        if "cloudflared.exe" in out:
            return
    except Exception:
        pass

    exe_path = os.path.join(BASE_DIR, "bin", "cloudflared.exe")
    if os.path.exists(exe_path):
        log_file = os.path.join(BASE_DIR, "data", "tunnel.log")
        logger.info(f"Starting cloudflared tunnel to localhost:{port}...")
        with open(log_file, "w", encoding="utf-8") as f_log:
            subprocess.Popen([exe_path, "tunnel", "--url", f"http://localhost:{port}"],
                             stdout=f_log, stderr=subprocess.STDOUT)


class AIRestHandler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, data: dict):
        try:
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, HEAD")
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            pass

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, HEAD")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html"):
            html_path = os.path.join(BASE_DIR, "web", "index.html")
            if os.path.exists(html_path):
                with open(html_path, "r", encoding="utf-8") as f:
                    content = f.read()
                tunnel_url = get_active_tunnel_url()
                content = content.replace("https://ivory-stuart-paso-implied.trycloudflare.com", tunnel_url)
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(content.encode("utf-8"))
            else:
                self.send_response(404)
                self.end_headers()
            return

        if path == "/manifest.json":
            m_path = os.path.join(BASE_DIR, "web", "manifest.json")
            if os.path.exists(m_path):
                with open(m_path, "rb") as f:
                    data = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/manifest+json")
                self.end_headers()
                self.wfile.write(data)
                return

        if path == "/sw.js":
            sw_path = os.path.join(BASE_DIR, "web", "sw.js")
            if os.path.exists(sw_path):
                with open(sw_path, "rb") as f:
                    data = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/javascript")
                self.end_headers()
                self.wfile.write(data)
                return

        if path in ("/icon-192.png", "/icon-512.png", "/phone_qr.png"):
            icon_file = path.strip("/")
            icon_path = os.path.join(BASE_DIR, "web", icon_file)
            if os.path.exists(icon_path):
                with open(icon_path, "rb") as f:
                    data = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.end_headers()
                self.wfile.write(data)
                return

        if path == "/api/status":
            self._send_json(200, {
                "server": "NEXUS Private AI Brain",
                "status": "ONLINE",
                "local_ip": get_local_ip(),
                "port": 5050,
                "gpu": "NVIDIA GeForce RTX 4050 Laptop GPU (6GB VRAM)",
                "ram": "16 GB",
                "default_pin": PIN
            })
            return

        if path == "/api/tunnel_info":
            tunnel_url = get_active_tunnel_url()
            self._send_json(200, {
                "tunnel_url": tunnel_url,
                "local_ip": get_local_ip(),
                "port": 5050,
                "pin": PIN,
                "qr_path": "/phone_qr.png"
            })
            return

        self._send_json(404, {"error": "Not Found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            payload = json.loads(body)
        except Exception:
            payload = {}

        if path == "/api/verify_pin":
            entered_pin = str(payload.get("pin", "")).strip()
            if entered_pin == PIN:
                token = secrets.token_hex(16)
                VALID_TOKENS.add(token)
                self._send_json(200, {"success": True, "token": token})
            else:
                self._send_json(401, {"success": False, "message": "Incorrect PIN"})
            return

        if path == "/api/chat":
            # Security verification
            auth_header = self.headers.get("Authorization", "").replace("Bearer ", "").strip()
            if auth_header not in VALID_TOKENS and len(VALID_TOKENS) > 0:
                self._send_json(403, {"success": False, "message": "Unauthorized. Please unlock with your PIN."})
                return

            prompt = payload.get("prompt", "").strip()
            model_choice = payload.get("model", "gemini")

            if not prompt:
                self._send_json(400, {"success": False, "message": "Empty prompt"})
                return

            logger.info(f"Processing query via [{model_choice}]: '{prompt[:60]}...'")

            if model_choice == "ollama":
                res = query_ollama_local(prompt)
            else:
                res = query_gemini_cloud(prompt)

            self._send_json(200, res)
            return

        self._send_json(404, {"error": "Not Found"})


def run_server(port: int = 5050):
    ensure_cloudflared_running(port)
    tunnel_url = get_active_tunnel_url()
    update_qr_code(tunnel_url)

    server = ThreadedServer(("0.0.0.0", port), AIRestHandler)
    print("\n" + "=" * 60)
    print(" [NEXUS] PRIVATE AI BRAIN SERVER RUNNING")
    print("=" * 60)
    print(f"  PC Browser:    http://localhost:{port}")
    print(f"  Phone App URL: {tunnel_url}")
    print(f"  Security PIN:  {PIN}")
    print(f"  Hardware:      NVIDIA RTX 4050 GPU + 16GB RAM")
    print(f"  Engines:       Local RTX 4050 (Qwen3) + Cloud Gemini 3.5")
    print("=" * 60 + "\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        server.server_close()


if __name__ == "__main__":
    run_server(5050)
