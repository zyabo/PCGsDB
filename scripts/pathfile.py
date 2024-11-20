
import os

def parse_path(path):
    # Get the file name and extension
    file_name_with_ext = os.path.basename(path)
    file_name, file_ext = os.path.splitext(file_name_with_ext)
    part_char = file_name[3]
    return part_char, file_name

