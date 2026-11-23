"""App mínima para probar la skill en 5 minutos. Uso: python app.py [puerto]"""
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

if __name__ == "__main__":
    puerto = int(sys.argv[1]) if len(sys.argv) > 1 else 8090
    ThreadingHTTPServer(("127.0.0.1", puerto), SimpleHTTPRequestHandler).serve_forever()
