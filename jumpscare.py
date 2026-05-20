import time
import threading
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
import vlc  # python-vlc
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER

# === CONFIG ===
VIDEO_PATH = r"C:\path\to\your\jumpscare.mp4"  # Use raw string for Windows paths
PORT = 8080
TRIGGER_PATH = "/scare"  # Change to something random like /x7k9p2m

def set_system_volume(percent=100):
    """Crank system volume to max"""
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, 0, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMasterVolumeLevelScalar(percent / 100.0, None)  # 0.0 to 1.0
    volume.SetMute(0, None)  # Unmute

def trigger_scare():
    try:
        print("🚨 Jump scare triggered!")
        
        # 1. Crank the volume
        set_system_volume(100)
        
        # 2. Play with VLC via python-vlc (precise control)
        instance = vlc.Instance('--fullscreen', '--no-video-title-show', '--quiet')
        player = instance.media_player_new()
        media = instance.media_new(VIDEO_PATH)
        player.set_media(media)
        
        player.play()
        
        # Wait for video to finish (plus a tiny buffer)
        time.sleep(0.5)  # Let it start
        duration = player.get_length() / 1000.0  # in seconds
        if duration > 0:
            time.sleep(duration + 1)  # Play full duration + 1s safety
        else:
            # Fallback: sleep a fixed time if duration detection fails
            time.sleep(25)
        
        # 3. Close everything
        player.stop()
        player.release()
        instance.release()
        
        # Optional: Restore reasonable volume after
        # set_system_volume(50)
        
        print("✅ Scare finished and cleaned up.")
        
    except Exception as e:
        print("Error:", e)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == TRIGGER_PATH:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Triggered!")
            threading.Thread(target=trigger_scare, daemon=True).start()
            return
        self.send_response(404)
        self.end_headers()

def run_server():
    server = HTTPServer(('', PORT), Handler)
    print(f"✅ Jump scare server running on port {PORT}. Trigger: http://YOUR_IP:{PORT}{TRIGGER_PATH}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()