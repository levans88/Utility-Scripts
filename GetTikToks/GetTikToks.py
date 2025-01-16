import os
import subprocess
from datetime import datetime
import re

# Define paths directly with Ignore/ included
url_list = "Ignore/like_list_cleaned.txt"
cookies_file = "Ignore/cookies.txt"
output_dir = "F:/Temp/2"
log_dir = "Ignore/logs"
yt_dlp_path = "C:/Storage/Portable/youtube-dlp/yt-dlp.exe"  # Full path to youtube-dlp executable

# Create necessary directories if they don't exist
os.makedirs(output_dir, exist_ok=True)
os.makedirs(log_dir, exist_ok=True)

# Generate a timestamp for the error log
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
error_log = f"{log_dir}/error_log_{timestamp}.txt"

# Sanitize the output directory and file template
output_template = f"{output_dir}/" + "%(upload_date)s - %(id)s - %(uploader)s - %(title).100s.%(ext)s"

# yt-dlp options
yt_dlp_options = [
    yt_dlp_path,  # Use the full path to youtube-dlp
    "--format", "(bestvideo[height<=1080]+bestaudio/best)[ext=mp4]",
    "--merge-output-format", "mp4",
    "--write-info-json",
    "--output", output_template,  # Use the sanitized output template
    "--write-thumbnail",
    "--add-metadata",
    "--embed-thumbnail",
    "--cookies", cookies_file,
    "--sleep-interval", "2",
    "--max-sleep-interval", "5",
    "--limit-rate", "500K",
    "-a", url_list
]

# Run yt-dlp and capture output
try:
    with open(error_log, "w") as log_file:
        subprocess.run(yt_dlp_options, stdout=log_file, stderr=subprocess.STDOUT, check=True)
    print(f"All downloads completed! Files saved in: {output_dir}")
    print(f"Errors (if any) are logged in: {error_log}")
except subprocess.CalledProcessError:
    print(f"Error occurred! Check the log file: {error_log}")
