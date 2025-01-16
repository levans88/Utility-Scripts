# Input and output file paths
input_file = "Ignore/Like List.txt"  # Replace with your input file name
output_file = "Ignore/like_list_cleaned.txt"  # Output file with cleaned list of URLs

# Open the input file and process it
with open(input_file, "r") as infile, open(output_file, "w") as outfile:
    for line in infile:
        # Strip whitespace and check if the line starts with "Link: https"
        line = line.strip()
        if line.startswith("Link: https"):
            # Extract the URL part of the line (everything after "Link: ")
            url = line[len("Link: "):]
            outfile.write(url + "\n")  # Write the extracted URL to the output file

print(f"URLs extracted and saved to {output_file}")
