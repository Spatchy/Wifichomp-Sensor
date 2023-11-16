import os
import subprocess
import re
import time
from dotenv import load_dotenv
import socketio

load_dotenv()

sio = socketio.Client()

@sio.event
def connect():
    print("Connected to the server")

@sio.event
def disconnect():
    print("Disconnected from the server")

def scan_wifi_networks():
    try:
        # Scan for nearby networks
        scan_result = subprocess.check_output(["sudo", "iwlist", os.environ.get("INTERFACE_LABEL"), "scan"], universal_newlines=True)

        # Extract SSID and Signal level
        networks = re.findall(r'ESSID:"(.*?)"\s*.*?Signal level=(-\d+) dBm', scan_result, re.DOTALL)
        networks = [(ssid if ssid else "[Hidden Network]", signal) for ssid, signal in networks]

        sorted_networks = sorted(networks, key=lambda x: int(x[1]))
        sorted_networks.reverse()

        sio.emit('wifiData', {"networks": sorted_networks, "token": os.environ.get("WEB_SERVER_API_TOKEN")})

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    try:
        sio.connect(os.environ.get("WEB_SERVER_ADDRESS"))

        while True:
            scan_wifi_networks()
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nExiting...")
        sio.disconnect()