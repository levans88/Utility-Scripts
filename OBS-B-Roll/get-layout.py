from screeninfo import get_monitors

def get_display_boundaries():
    display_boundaries = {}
    for i, monitor in enumerate(get_monitors(), start=1):
        # Use the display number as the key
        display_name = str(i)
        display_boundaries[display_name] = (
            monitor.x, monitor.y,
            monitor.x + monitor.width,
            monitor.y + monitor.height
        )
    return display_boundaries

# Get the display boundaries
display_boundaries_rdp = get_display_boundaries()

# Format the output as per your requirement
formatted_output = "display_boundaries_rdp = {\n"
for key, value in display_boundaries_rdp.items():
    formatted_output += f"    '{key}': {value},\n"
formatted_output = formatted_output.rstrip(",\n") + "\n}"

# Print the formatted output
print(formatted_output)
