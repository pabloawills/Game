#!/usr/bin/env python3
"""Portal web local para lanzar `juego.py` desde una página HTML."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import subprocess
import sys

HOST = "127.0.0.1"
PORT = 8080
BASE_DIR = Path(__file__).resolve().parent


class PortalHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        if self.path.rstrip("/") == "/launch":
            self.send_response(204)
            self.end_headers()
            return
        self.send_error(404, "Ruta no encontrada")

    def launch_game(self):
        game_file = BASE_DIR / "juego.py"
        if not game_file.exists():
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"No se encontro juego.py en el directorio actual.")
            return

        try:
            subprocess.Popen([sys.executable, str(game_file)], cwd=str(BASE_DIR))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Juego abierto. Revisa tu escritorio/ventanas activas.")
        except Exception as exc:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Error al lanzar juego: {exc}".encode("utf-8"))

    def do_POST(self):
        if self.path.rstrip("/") != "/launch":
            self.send_error(404, "Ruta no encontrada")
            return
        self.launch_game()

    def do_GET(self):
        if self.path.rstrip("/") == "/launch":
            self.launch_game()
            return
        super().do_GET()


class ReusableThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True


def main():
    print(f"Portal disponible en http://{HOST}:{PORT}", flush=True)
    print("Pulsa Ctrl+C para cerrar.", flush=True)

    handler = partial(PortalHandler, directory=str(BASE_DIR))
    try:
        server = ReusableThreadingHTTPServer((HOST, PORT), handler)
    except OSError as exc:
        print(
            (
                f"No se pudo iniciar el servidor en {HOST}:{PORT}. "
                f"Error del sistema: {exc}. "
                "Cierra el proceso que ya usa ese puerto o cambia PORT."
            ),
            file=sys.stderr,
            flush=True,
        )
        raise SystemExit(1) from exc

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
