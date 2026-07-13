"""
Local server for the teacher AR demo.

Double-click the root launcher:
  一键启动教师Demo.bat

The script serves this folder on localhost, prints a LAN address for phone
testing, and opens the desktop preview automatically. Camera permission is
still controlled by the browser.
"""

from __future__ import annotations

import http.server
import ipaddress
import os
import re
import socket
import subprocess
import threading
import time
import webbrowser
from pathlib import Path


START_PORT = 8080
END_PORT = 8090
DEMO_DIR = Path(__file__).resolve().parent
DEFAULT_PAGE = "multi-spot-template.html"


class DemoHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DEMO_DIR), **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Permissions-Policy", "camera=*, microphone=*")
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        super().end_headers()


def is_lan_ip(value: str) -> bool:
    try:
        ip = ipaddress.ip_address(value)
    except ValueError:
        return False

    if ip.is_loopback or ip.is_link_local:
        return False

    return (
        value.startswith("10.")
        or value.startswith("192.168.")
        or re.match(r"^172\.(1[6-9]|2\d|3[0-1])\.", value) is not None
    )


def get_lan_ips() -> list[str]:
    candidates: list[str] = []

    try:
        for item in socket.gethostbyname_ex(socket.gethostname())[2]:
            candidates.append(item)
    except OSError:
        pass

    try:
        completed = subprocess.run(
            ["ipconfig"],
            capture_output=True,
            check=False,
        )
        output = completed.stdout.decode("utf-8", errors="ignore")
        candidates.extend(re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", output))
    except OSError:
        pass

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            candidates.append(sock.getsockname()[0])
    except OSError:
        pass

    unique: list[str] = []
    for ip in candidates:
        if is_lan_ip(ip) and ip not in unique:
            unique.append(ip)

    return unique


def find_available_port(start: int = START_PORT, end: int = END_PORT) -> int:
    for port in range(start, end + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as test_socket:
            try:
                test_socket.bind(("0.0.0.0", port))
                return port
            except OSError:
                continue
    raise RuntimeError(
        f"Ports {start}-{end} are busy. Close other local servers and try again."
    )


def open_browser_later(url: str) -> None:
    def _open() -> None:
        time.sleep(0.8)
        webbrowser.open(url)

    threading.Thread(target=_open, daemon=True).start()


def main() -> None:
    lan_ips = get_lan_ips()
    port = find_available_port()
    desktop_url = f"http://127.0.0.1:{port}/{DEFAULT_PAGE}"
    phone_urls = [f"http://{ip}:{port}/{DEFAULT_PAGE}" for ip in lan_ips]

    print("=" * 64)
    print("  AR Campus Guide - Teacher Demo Server")
    print("=" * 64)
    print()
    print(f"  Desktop preview: {desktop_url}")
    if phone_urls:
        print("  Phone preview:")
        for url in phone_urls:
            print(f"    - {url}")
    else:
        print("  Phone preview: connect the phone to the same Wi-Fi, then use ipconfig")
        print(f"                 to find this computer's IPv4 address and add :{port}/index.html")
    print()
    print("  Notes:")
    print("  - Keep this window open while testing.")
    print("  - Browser camera permission is required for AR preview.")
    print("  - localhost usually supports camera access.")
    print("  - For phone testing, HTTPS deployment is the most reliable option.")
    print()
    print("  Press Ctrl+C to stop the server.")
    print("=" * 64)

    if os.environ.get("NO_BROWSER") != "1":
        open_browser_later(desktop_url)

    server = http.server.ThreadingHTTPServer(("0.0.0.0", port), DemoHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
