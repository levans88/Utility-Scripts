#!/usr/bin/python

# Caja script to create launchers on desktop without hand editing .desktop files
# or manually setting options by "mate-desktop-item-edit ./ --create-new"
#
# - Retrieves mime-type based on selected file extension
# - Retrieves application for execution based on mime-type
# - Retrieves icon based on mime-type
# - Creates launcher on current user's desktop
#
# The application name for .tar files isn't found until mime_apps_3, 
# where it's written as "org.gnome.FileRoller.desktop", which is 
# found in "/usr/share/app-install/desktop" as one of the following:
#   "file-roller:file-roller.desktop"
#   "file-roller:org.gnome.FileRoller.desktop"
#
# The other application shown this way is Totem. I don't currently 
# understand the ":" in the name. Neither apps launch from terminal.
#
# What's more odd is that tar files are handled by "engrampa" when
# opened directly. Shortcuts to tar files aren't important, but I 
# don't know what else might be affected.
#
# Todo:
# - Override .tar launcher exec with Engrampa as application (discovered that
#   Engrampa is a Caja extension). No one needs a launcher for this but still...
# - Simplify getting mime-type without using extension, use "file" command
#   (see get_mime_type function for example...)
#

import os
import stat
import datetime

debug = False
debug_path = "/home/user/Temp/"


# Output debug log file
def log(message):
    if debug == True:
        out = open(debug_path + "Auto-Create-Launcher-Debug.log", "a")
        out.write(str(datetime.datetime.now()).split('.')[0] + "\t\t" + message + "\n")
        out.close()


# Create and write contents of .desktop launcher file
def create_launcher(path, exec_string, icon_string):    
    header_string = "#!/usr/bin/env xdg-open"
    name_string = "Name=" + path.rpartition('/')[2]
    footer_string = "#Created by Auto-Create-Launcher.py"

    log("path = " + path)
    log("exec_string = " + exec_string)
    log("name_string = " + name_string)
    log("icon_string = " + icon_string)

    desktop_dest_path = os.path.expanduser("~/Desktop/") + path.rpartition('/')[2] + ".desktop"

    desktop_file = open(desktop_dest_path, "w+")

    desktop_file.write(header_string + "\n\n" + "[Desktop Entry]" + "\n" + "Type=Application" + "\n" + exec_string + "\n" + name_string + "\n" + icon_string + "\n" + footer_string)

    desktop_file.close()
    set_exec_permission(desktop_dest_path)
    
    log("Launcher created successfully.")

# Set file as executable to avoid prompt about "untrusted"...
def set_exec_permission(desktop_dest_path):
    # st.mode is offered by autocomplete but that's wrong, use st.st_mode
    # S_IXUSR and S_IRGRP and S_IXOTH make the file executable across the board
    # S_IEXEC would make it executable only by the user
    #
    #https://stackoverflow.com/questions/12791997/how-do-you-do-a-simple-chmod-x-from-within-python
    #
    desktop_file_name = desktop_dest_path
    st = os.stat(desktop_file_name)
    
    os.chmod(desktop_file_name, st.st_mode | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXOTH)


# Get mime-type based on file extension
def get_mime_type(path):
    mime_type = ""

    # Get file extension
    file_extension = path.rpartition('.')[2]
    log("file_extension = " + file_extension)

    # If the file didn't have an extension...
    if file_extension == path:
        log("file_extension == path")
        # Should use this command to simplify script, was not previously aware...
        mime_type = os.popen("file --mime-type -b " + path).read().rstrip()
        log("mime_type = " + mime_type)
        return mime_type

    # If the file had an extension, look it up...
    if os.path.isfile("/etc/mime.types"):
        log("/etc/mime.types file found.")
        mime_types_file = open("/etc/mime.types", "r")
        
        index = 0    

        # Load mime.types file into memory
        for line in mime_types_file:
            
            # Get string after first whitespace as right_column
            line_array = line.split("\t")
            right_column = ""

            i = 1
            while i < len(line_array):
                right_column += line_array[i] + " "
                i += 1

            # Find space+file_extension or tab+file_extension in right_column
            index = right_column.rfind(" " + file_extension + " ")
            if index == -1:
                index = right_column.rfind("\t" + file_extension + " ")
            if index == -1:
                index = right_column.rfind(" " + file_extension + "\n")
            if index == -1:
                index = right_column.rfind("\t" + file_extension + "\n")

            # If file_extension was found, get associated mime_type
            if index != -1:
                mime_type = line.split()[0]

                log("line = " + chr(34) + line.rstrip() + chr(34))
                log("mime_type = " + mime_type)

        mime_types_file.close()
    else:
        log("/etc/mime.types file not found.")

    return mime_type


def parse_mime_app_file(mime_file_path):
    app_name = ""
    if os.path.isfile(mime_file_path):
        log(mime_file_path + " file found.")
        
        file = open(mime_file_path, "r")
        
        # Split on equal sign, find app_name in right column
        for line in file:
            left_column = line.partition("=")[0]
            right_column = line.partition("=")[2].rstrip()
            
            if left_column == mime_type:
                app_name = right_column
                log("line = " + chr(34) + line.rstrip() + chr(34))
        log("app_name = " + app_name)

        file.close()
    else:
        log(mime_file_path + " file not found.")
    
    return app_name

# Get application for execution based on mime-type
def get_associated_application(mime_type): 
    app_name = ""
    mime_apps_1 = os.path.expanduser("~/.config/mimeapps.list")
    mime_apps_2 = os.path.expanduser("~/.local/share/applications/mimeapps.list")
    mime_apps_3 = "/usr/share/applications/defaults.list"

    # Open most relevant file first if found
    app_name = parse_mime_app_file(mime_apps_1)

    # Open second most relevant file if no application name was found
    if app_name is None or app_name is "":
        app_name = parse_mime_app_file(mime_apps_2)

    # Lastly, try defaults file if still no application has been found
    if app_name is None or app_name is "":
        app_name = parse_mime_app_file(mime_apps_3)

    if app_name is None or app_name is "":
        log("No associated application for mime-type: " + chr(34) + mime_type + chr(34))
    
    return app_name

# Get path with filename (unless folder), default key to "None" if none selected
path = os.environ.get('CAJA_SCRIPT_SELECTED_FILE_PATHS', None)
log("----------Start of log.----------")

if path is not None and path is not "":
    path = path.rstrip()
    log("Path is not None or empty.")
    log("path = " + path)

    # If the path is a folder...
    if os.path.isdir(path):  
        log("Path is a directory.")

        exec_string = "Exec=caja " + chr(34) + path + chr(34)
        icon_string = "Icon=folder_color_orange"
        
        create_launcher(path, exec_string, icon_string)
    # If the path is a file...
    else:
        log("Path is a file.")
        
        # Get mime-type
        mime_type = get_mime_type(path)
        app_name = ""
        exec_string = ""

        # *** Override app_name's and exec_string's here ***
        #
        # Override app_name and exec_string for executable files
        if mime_type == "application/x-executable":
            app_name = path.rpartition("/")[2].rstrip()
            exec_string = "Exec=" + app_name
        else:
            # Otherwise assign retrieved app_name's and exec_string's here...
            if mime_type is not None and mime_type is not "":
                # Get application for execution based on mime-type
                app_name = get_associated_application(mime_type).partition(".")[0]

                # Override app_name for sublime_text
                if app_name == "sublime_text":
                    app_name = "/opt/sublime_text/sublime_text"

                exec_string = "Exec=" + app_name + " " + chr(34) + path + chr(34)
        
        if app_name is not None and app_name is not "":
            # Set icon based on mime-type
            icon_string = "Icon=" + mime_type.replace("/", "-")

            # Create launcher
            create_launcher(path, exec_string, icon_string)
else:
    log("Path is None or empty.")