#!/usr/bin/env python3
import os
import sys
import logging
import threading
import subprocess
from dotenv import load_dotenv
import time
import signal
from pystray import Icon, MenuItem as Item, Menu
from PIL import Image

# Ensure the logs directory exists
os.makedirs('logs', exist_ok=True)

load_dotenv()

logging.basicConfig(
    filename='logs/kap.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ss-local')

class ShadowsocksClient:
    def __init__(self):
        self.process = None
        self.running = False
        self.local_addr = os.getenv('local_addr', 'socks5://127.0.0.1:1080')
        self.remote_server = os.getenv('remote_addr', '')

    def start_helper(self, icon=None):
        if self.running:
            logger.info("Already running")
            return

        cmd = [sys.executable, "-m", "pproxy", "-l", self.local_addr, "-r", self.remote_server, "-vv"]
        logger.info(f"Starting: {' '.join(cmd)}")

        try:
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    startupinfo=startupinfo,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1
                )

            # Log output in real time
            def log_pipe(pipe, level):
                for line in iter(pipe.readline, ''):
                    logger.log(level, f"pproxy: {line.strip()}")
            threading.Thread(target=log_pipe, args=(self.process.stdout, logging.INFO), daemon=True).start()
            threading.Thread(target=log_pipe, args=(self.process.stderr, logging.ERROR), daemon=True).start()

            time.sleep(2)
            if self.process.poll() is None:
                self.running = True
                logger.info(f"✅ Proxy started on {self.local_addr}")
                if icon:
                    icon.title = "Active"
                threading.Thread(target=self._monitor_process, daemon=True).start()
            else:
                logger.error("Process exited immediately")
                self.process = None
        except Exception as e:
            logger.exception(f"Start failed: {e}")
            self.process = None

    def _monitor_process(self):
        if self.process:
            self.process.wait()
            if self.running:
                logger.warning("Proxy terminated unexpectedly")
                self.running = False

    def stop_helper(self, icon=None):
        if self.process and self.running:
            logger.info("Stopping...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            self.process = None
            self.running = False
            logger.info("Stopped")
            if icon:
                icon.title = "Stopped"
        else:
            logger.info("Not running")

    def exit_app(self, icon=None):
        self.stop_helper(icon)
        if icon:
            icon.stop()
        # Ensure the script ends
        os._exit(0)

def main():
    client = ShadowsocksClient()
    image = Image.new('RGB', (64, 64), color="#f3e820")
    menu = Menu(
        Item('Start', client.start_helper),
        Item('Stop', client.stop_helper),
        Item('Exit', client.exit_app)
    )
    icon = Icon("kap_client", image, "kapHelper", menu)

    # Signal handler for graceful shutdown
    def signal_handler(sig, frame):
        print("\nInterrupt received, shutting down...")
        client.exit_app(icon)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    icon.run()

if __name__ == "__main__":
    main()