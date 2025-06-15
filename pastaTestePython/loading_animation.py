import sys
import time
import threading

class LoadingAnimation:
    def __init__(self):
        self._loading = False
        self._thread = None
        
    def _animate(self):
        while self._loading:
            for i in range(4):
                if not self._loading: break
                sys.stdout.write('\rProcessando' + '.' * i + '   ')
                sys.stdout.flush()
                time.sleep(0.3)
        sys.stdout.write('\r' + ' ' * 20 + '\r')
    
    def start(self):
        self._loading = True
        self._thread = threading.Thread(target=self._animate, daemon=True)
        self._thread.start()
    
    def stop(self):
        self._loading = False
        if self._thread:
            self._thread.join(timeout=0.5)