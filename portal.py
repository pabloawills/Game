#!/usr/bin/env python3
"""Portal web local para lanzar `juego.py` desde una página HTML."""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import subprocess
import sys

HOST = "127.0.0.1"
PORT = 8080
BASE_DIR = Path(__file__).resolve().parent


class PortalHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/launch":
            self.send_error(404, "Ruta no encontrada")
            return

        game_file = BASE_DIR / "juego.py"
        if not game_file.exists():
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"No se encontro juego.py en el directorio actual.")
            return

        try:
            # Se lanza en proceso independiente para no bloquear el servidor HTTP.
            subprocess.Popen([sys.executable, str(game_file)], cwd=str(BASE_DIR))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Juego abierto. Revisa tu escritorio/ventanas activas.")
        except Exception as exc:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Error al lanzar juego: {exc}".encode("utf-8"))


def main():
    print(f"Portal disponible en http://{HOST}:{PORT}")
    print("Pulsa Ctrl+C para cerrar.")
    server = ThreadingHTTPServer((HOST, PORT), PortalHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
