import time
from obswebsocket import obsws, requests
from pynput import mouse, keyboard
import ctypes

# OBS WebSocket connection details
password_file_path = r"C:\Temp\obs-web-socket-server.txt"
with open(password_file_path, "r") as file:
    password = file.read().strip()

host = 'localhost'
port = 4455

# Define boundaries for each display or quadrant
display_boundaries = {
    "4k1": (0, 0, 1920, 1080),
    "4k2": (1920, 0, 3840, 1080),
    "4k3": (0, 1080, 1920, 2160),
    "4k4": (1920, 1080, 3840, 2160),
    "Portrait1": (-1080, 0, 0, 1920),
    "Portrait2": (3840, 0, 4920, 1920),
    "Portrait3": (4920, 0, 6000, 1920),
}

display_boundaries_rdp = {
    '1': (3000, -458, 4080, 1462), 
    '2': (1920, -458, 3000, 1462), 
    '3': (0, 0, 1920, 1080), 
    '4': (0, 1080, 1920, 2160)
}

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

# Check if the current session is an RDP session
def is_rdp_session():
    user32 = ctypes.windll.user32
    return bool(user32.GetSystemMetrics(0x1000))  # 0x1000 is SM_REMOTESESSION

# Set display boundaries based on the current session type
def setup_display_boundaries():
    global display_boundaries
    if IsRDPSession:
        display_boundaries = display_boundaries_rdp
        print("RDP session detected, using RDP display boundaries.")
    else:
        print("Local session detected, using local display boundaries.")

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
        # Use SetCurrentScene for compatibility with OBS WebSocket v4.x
        # scenes = ws.call(requests.GetSceneList())
        # dd(response.getScenes())
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
    exit()

# Run the input listeners
if __name__ == "__main__":
    print("Starting OBS automation script.")
    IsRDPSession = is_rdp_session()
    setup_display_boundaries()
    setup_listeners()

# Disconnect from OBS WebSocket on exit
ws.disconnect()
print("Disconnected from OBS WebSocket.")
