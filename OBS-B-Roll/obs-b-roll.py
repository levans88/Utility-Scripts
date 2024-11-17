import json
import os
import getpass
from obswebsocket import obsws, requests
from pynput import mouse, keyboard
from screeninfo import get_monitors
import time

# Read OBS WebSocket password from an external file
password_file_path = r"C:\Temp\obs-web-socket-server.txt"
with open(password_file_path, "r") as file:
    password = file.read().strip()  # Remove any extra whitespace or newlines

# OBS WebSocket connection details
host = 'localhost'
port = 4455

# Determine the username automatically
username = getpass.getuser()

# Automatically construct the OBS scene collection file path
scene_file_path = os.path.join(
    "C:\\Users", username, "AppData", "Roaming", "obs-studio", "basic", "scenes", "SceneCollection1.json"
)

# Establish connection to OBS WebSocket
ws = obsws(host, port, password)
ws.connect()

# Configuration variables
InactivityTimeout = 5  # 5 seconds inactivity threshold
LastInputTime = time.time()
IsRecording = False

# Detect displays, including RDP-connected displays
def detect_displays():
    display_configs = []
    for monitor in get_monitors():
        if monitor.width == 3840 and monitor.height == 2160:
            # Treat 4K display as four separate 1080p screens (quadrants)
            display_configs.extend([
                {"name": f"{monitor.name}_TL", "x": monitor.x, "y": monitor.y, "width": 1920, "height": 1080, "orientation": "landscape"},
                {"name": f"{monitor.name}_TR", "x": monitor.x + 1920, "y": monitor.y, "width": 1920, "height": 1080, "orientation": "landscape"},
                {"name": f"{monitor.name}_BL", "x": monitor.x, "y": monitor.y + 1080, "width": 1920, "height": 1080, "orientation": "landscape"},
                {"name": f"{monitor.name}_BR", "x": monitor.x + 1920, "y": monitor.y + 1080, "width": 1920, "height": 1080, "orientation": "landscape"}
            ])
        else:
            # Treat non-4K displays as single screens
            orientation = "portrait" if monitor.width < monitor.height else "landscape"
            display_configs.append({
                "name": monitor.name,
                "x": monitor.x,
                "y": monitor.y,
                "width": monitor.width,
                "height": monitor.height,
                "orientation": orientation
            })
    # Output detected display information
    for display in display_configs:
        print(display)
    return display_configs

# Modify OBS scene collection based on detected displays
def configure_scenes(display_configs):
    print("Configuring display capture sources in OBS based on detected displays...")

    # Get all scenes to find items and clear them
    scenes = ws.call(requests.GetSceneList()).getScenes()
    
    # Loop through each scene and delete all items within it
    for scene in scenes:
        scene_name = scene['sceneName']
        print(f"Deleting all sources in scene: {scene_name}")

        # Retrieve all items in the current scene
        scene_items_response = ws.call(requests.GetSceneItemList(sceneName=scene_name))
        scene_items = scene_items_response.getSceneItems() if scene_items_response else []

        # Check if there are scene items to delete
        if not scene_items:
            print(f"No sources found in scene: {scene_name}. Skipping deletion.")
            continue
        
        # Delete each item in the scene
        for item in scene_items:
            print(f"  Deleting source: {item['sourceName']}")
            ws.call(requests.RemoveSceneItem(sceneName=scene_name, sceneItemId=item['sceneItemId']))

    # Loop through each display and configure a new display capture source
    for display in display_configs:
        # Clean up the name to remove any extra characters
        display_name = display["name"].replace("\\\\.\\", "")

        # Log information about the source being added
        print(f"Configuring source: {display_name}")
        print(f"  Position: ({display['x']}, {display['y']})")
        print(f"  Size: ({display['width']}x{display['height']})")
        print(f"  Orientation: {display['orientation']}")

        # Create a new display capture source in the first scene in the collection
        main_scene = scenes[0]['sceneName']
        ws.call(requests.CreateInput(
            sceneName=main_scene,
            inputName=display_name,
            inputKind="monitor_capture",
            inputSettings={"monitor": 0}  # Adjust this if multiple monitors are available
        ))

        # Set position and scale of the source
        ws.call(requests.SetSceneItemTransform(
            sceneName=main_scene,
            sceneItemId=ws.call(requests.GetSceneItemId(sceneName=main_scene, sourceName=display_name)).getSceneItemId(),
            transform={
                "position": {"x": display["x"], "y": display["y"]},
                "scale": {"x": 1.0, "y": 1.0} if display["orientation"] == "landscape" else {"x": 0.5, "y": 1.0}
            }
        ))
    
    print("Finished configuring display sources.")

# Start and stop recording functions
def start_recording():
    global IsRecording
    if not IsRecording:
        ws.call(requests.StartRecord())
        IsRecording = True

def stop_recording():
    global IsRecording
    if IsRecording:
        ws.call(requests.StopRecord())
        IsRecording = False

# Update LastInputTime on activity, accepting all arguments required by pynput
def on_activity(*args):
    global LastInputTime
    LastInputTime = time.time()

# Monitor for inactivity and control recording
def monitor_inactivity():
    global LastInputTime
    while True:
        if time.time() - LastInputTime > InactivityTimeout:
            stop_recording()
        time.sleep(1)

# Set up input listeners for mouse and keyboard
def setup_listeners():
    with mouse.Listener(on_move=on_activity, on_click=on_activity) as ml, \
         keyboard.Listener(on_press=on_activity) as kl:
        monitor_inactivity()

# Run the full setup
if __name__ == "__main__":
    # Detect displays and configure OBS scenes
    display_configs = detect_displays()
    configure_scenes(display_configs)

    # Start monitoring input and controlling OBS recording
    setup_listeners()

# Disconnect from OBS WebSocket on exit
ws.disconnect()
