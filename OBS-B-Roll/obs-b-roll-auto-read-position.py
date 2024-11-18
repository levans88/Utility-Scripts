
# NOTE: This does not work because OBS does not actually know the monitor positions.


import time
from obswebsocket import obsws, requests
from pynput import mouse, keyboard
import json
import os
import sys
import ctypes

# Define path to OBS scene collection files
scene_directory = os.path.join(os.getenv('APPDATA'), 'obs-studio', 'basic', 'scenes')

# OBS WebSocket connection details
password_file_path = r"C:\Temp\obs-web-socket-server.txt"
with open(password_file_path, "r") as file:
    password = file.read().strip()

host = 'localhost'
port = 4455

# Inactivity timeout and tracking variables
InactivityTimeout = 5  # 5 seconds
LastInputTime = time.time()
IsRecording = False
CurrentScene = None
LastActiveDisplay = None
IsRDPSession = False

# Connect to OBS WebSocket
ws = obsws(host, port, password)
ws.connect()

# Function to retrieve display boundaries from OBS files
def get_display_boundaries_from_files():
    boundaries = {}
    # Determine which file to use based on session type
    scene_file = 'SceneCollection2.json' if is_rdp_session() else 'SceneCollection1.json'
    print(f"Selected scene file: {scene_file}")

    # Full path to the scene file
    scene_path = os.path.join(scene_directory, scene_file)

    print(f"Opening scene file: {scene_path}")
    # Load the scene collection file
    with open(scene_path, 'r') as file:
        data = json.load(file)
        print(f"Loaded JSON data from {scene_file}")

        # Iterate over each scene defined in 'scene_order'
        for scene_ref in data['scene_order']:
            scene_name = scene_ref['name']
            print(f"Processing scene: {scene_name}")

            # Find the actual scene details in 'sources' matching the scene name
            scene = next((s for s in data['sources'] if s['name'] == scene_name and s['id'] == 'scene'), None)
            if scene and 'settings' in scene and 'items' in scene['settings']:
                for item in scene['settings']['items']:
                    source_name = item['name']
                    x = item['pos']['x']
                    y = item['pos']['y']
                    width = item['scale']['x'] * item['bounds']['x']
                    height = item['scale']['y'] * item['bounds']['y']

                    boundaries[source_name] = (x, y, x + width, y + height)
                    print(f"Source '{source_name}' in scene '{scene_name}' boundaries set to: (x1={x}, y1={y}, x2={x + width}, y2={y + height})")
            else:
                print(f"No items found for scene '{scene_name}' or scene details are missing.")

    print("Completed loading display boundaries from files.")
    return boundaries

def is_rdp_session():
    user32 = ctypes.windll.user32
    return bool(user32.GetSystemMetrics(0x1000))  # 0x1000 is SM_REMOTESESSION

# Recording controls
def start_recording():
    global IsRecording
    if not IsRecording:
        ws.call(requests.StartRecord())
        IsRecording = True
        print("Recording started.")

def stop_recording():
    global IsRecording
    if IsRecording:
        ws.call(requests.StopRecord())
        IsRecording = False
        print("Recording stopped.")

# Scene switching based on input activity on specific displays/quadrants
def switch_scene(scene_name):
    global CurrentScene
    if scene_name != CurrentScene:
        ws.call(requests.SetCurrentProgramScene(sceneName=scene_name))
        CurrentScene = scene_name
        print(f"Switched to scene: {scene_name}")

# Detect the active display based on mouse position
def detect_active_display():
    # Get the current mouse position
    mouse_position = mouse.Controller().position

    # Determine which display the mouse is on by checking boundaries
    for display_name, (x1, y1, x2, y2) in display_boundaries.items():
        if x1 <= mouse_position[0] < x2 and y1 <= mouse_position[1] < y2:
            print(f"Mouse detected on display: {display_name}")
            return display_name
    print("Mouse is not on any configured display.")
    return None

# Monitor inactivity and control recording based on display-specific input
def monitor_inactivity():
    global LastInputTime, LastActiveDisplay
    while True:
        active_display = detect_active_display()  # Determine the current active display
        
        # Only switch scenes if the active display has changed
        if active_display != LastActiveDisplay:
            LastActiveDisplay = active_display
            if active_display:
                switch_scene(active_display)
        
        # Start or continue recording if activity is detected
        if time.time() - LastInputTime <= InactivityTimeout:
            print("Input detected, checking recording status.")
            start_recording()
        
        # Stop recording after InactivityTimeout of no activity
        elif time.time() - LastInputTime > InactivityTimeout:
            print("No input detected, stopping recording.")
            stop_recording()
        
        time.sleep(1)

# Monitor input activity and update LastInputTime
def on_activity(*args):
    global LastInputTime
    LastInputTime = time.time()
    print("Activity detected, updating LastInputTime.")

# Input listeners
def setup_listeners():
    print("Setting up input listeners...")
    with mouse.Listener(on_move=on_activity, on_click=on_activity) as ml, \
         keyboard.Listener(on_press=on_activity) as kl:
        monitor_inactivity()

def dd(data):
    print(data)
    sys.exit()

# Run the input listeners
if __name__ == "__main__":
    print("Starting OBS automation script.")
    IsRDPSession = is_rdp_session()
    display_boundaries = get_display_boundaries_from_files()  # Load display boundaries once at startup
    setup_listeners()

# Disconnect from OBS WebSocket on exit
ws.disconnect()
print("Disconnected from OBS WebSocket.")
