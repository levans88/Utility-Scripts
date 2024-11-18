from screeninfo import get_monitors

def get_display_boundaries():
    display_boundaries = {}
    for i, monitor in enumerate(get_monitors(), start=1):
        display_name = f"Display{i}"
        display_boundaries[display_name] = (
            monitor.x, monitor.y,
            monitor.x + monitor.width,
            monitor.y + monitor.height
        )
    return display_boundaries

display_boundaries_rdp = get_display_boundaries()
print(display_boundaries_rdp)
