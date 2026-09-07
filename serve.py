#!/usr/bin/env python3
"""
BEEDATA – Live Reload Development Server
Uruchamia lokalny serwer HTTP na porcie 8000 i automatycznie odświeża przeglądarkę
przy każdej zapisanej zmianie w plikach projektu (HTML, CSS, JS, grafiki).
Zero zależności zewnętrznych (wykorzystuje wyłącznie standardową bibliotekę Pythona 3).
"""

import http.server
import os
import socketserver
import threading
import time
import webbrowser
from pathlib import Path

PORT = 8000
BASE_DIR = Path(__file__).resolve().parent

# Skrypt wstrzykiwany w locie do stron HTML w celach developerskich
LIVE_RELOAD_SNIPPET = b"""
<!-- Live Reload Snippet (Tylko lokalny podgl\xc4\x85d) -->
<script>
(() => {
  const connect = () => {
    const sse = new EventSource('/_live_reload_stream');
    sse.onopen = () => console.log('%c[LiveReload] Po\xc5\x82\xc4\x85czono z serwerem deweloperskim', 'color: #2563eb; font-weight: bold;');
    sse.onmessage = (e) => {
      if (e.data === 'reload') {
        console.log('%c[LiveReload] Wykryto zmian\xc4\x99 w pliku. Od\xc5\x9bwie\xc5\xbcam stron\xc4\x99...', 'color: #10b981; font-weight: bold;');
        window.location.reload();
      }
    };
    sse.onerror = () => {
      sse.close();
      setTimeout(connect, 1500);
    };
  };
  connect();
})();
</script>
</body>
"""

class FileWatcher:
    """Monitoruje katalog projektu pod kątem zmian w plikach."""
    def __init__(self, watch_path: Path):
        self.watch_path = watch_path
        self.subscribers = []
        self._lock = threading.Lock()
        self.last_mtimes = self._scan_mtimes()

    def _scan_mtimes(self):
        mtimes = {}
        for root, dirs, files in os.walk(self.watch_path):
            # Ignoruj katalogi gita i cache
            if '.git' in root or '.github' in root or '__pycache__' in root:
                continue
            for file in files:
                if file.endswith(('.html', '.css', '.js', '.json', '.png', '.jpg', '.jpeg', '.svg', '.webp')):
                    full_path = Path(root) / file
                    try:
                        mtimes[str(full_path)] = full_path.stat().st_mtime
                    except OSError:
                        pass
        return mtimes

    def subscribe(self):
        evt = threading.Event()
        with self._lock:
            self.subscribers.append(evt)
        return evt

    def unsubscribe(self, evt):
        with self._lock:
            if evt in self.subscribers:
                self.subscribers.remove(evt)

    def run(self):
        while True:
            time.sleep(0.3)
            current_mtimes = self._scan_mtimes()
            if current_mtimes != self.last_mtimes:
                self.last_mtimes = current_mtimes
                with self._lock:
                    for evt in self.subscribers:
                        evt.set()

watcher = FileWatcher(BASE_DIR)

class LiveReloadHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """Obsługuje żądania HTTP oraz strumień Server-Sent Events (SSE)."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE_DIR), **kwargs)

    def do_GET(self):
        if self.path == '/_live_reload_stream':
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            evt = watcher.subscribe()
            try:
                self.wfile.write(b": connected\n\n")
                self.wfile.flush()
                while True:
                    # Czekaj na zmianę lub wyślij keep-alive co 15 sekund
                    if evt.wait(timeout=15.0):
                        evt.clear()
                        self.wfile.write(b"data: reload\n\n")
                        self.wfile.flush()
                    else:
                        self.wfile.write(b": keepalive\n\n")
                        self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass
            finally:
                watcher.unsubscribe(evt)
            return

        return super().do_GET()

    def end_headers(self):
        # Blokuj pamięć podręczną przeglądarki podczas lokalnego developmentu
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        super().end_headers()

    def copyfile(self, source, outputfile):
        """Wstrzykuje skrypt nasłuchujący do stron HTML bez modyfikacji plików źródłowych na dysku."""
        content = source.read()
        target_path = self.path.split('?')[0]
        if target_path.endswith('.html') or target_path == '/' or target_path.endswith('/'):
            if b'</body>' in content:
                content = content.replace(b'</body>', LIVE_RELOAD_SNIPPET)
            else:
                content = content + LIVE_RELOAD_SNIPPET
        outputfile.write(content)

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

def main():
    # Uruchomienie wątku obserwującego pliki w tle
    watch_thread = threading.Thread(target=watcher.run, daemon=True)
    watch_thread.start()

    server = ThreadedHTTPServer(('127.0.0.1', PORT), LiveReloadHTTPHandler)
    url = f"http://localhost:{PORT}"
    print("=" * 65)
    print("  🚀 BEEDATA Live Reload Server uruchomiony!")
    print(f"  🔗 Adres: {url}")
    print("  👀 Obserwuję zmiany w plikach... (Zapisz plik, a strona odświeży się sama)")
    print("  ⏹️  Aby zatrzymać: wciśnij Ctrl + C")
    print("=" * 65)

    try:
        webbrowser.open(url)
    except Exception:
        pass

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Zatrzymano serwer deweloperski.")
        server.server_close()

if __name__ == '__main__':
    main()
