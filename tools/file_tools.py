import os

def create_file(file_path: str, content: str) -> str:
    """
    Creates a new file with the specified content.

    Args:
        file_path (str): The path and name of the file to create.
        content (str): The content to write to the file.
    """
    try:
        with open(file_path, 'w') as file:
            file.write(content)
        return f"File '{file_path}' created successfully."
    except Exception as e:
        return f"Error creating file '{file_path}': {e}"

def read_file(file_path: str) -> str:
    """
    Reads the content of a file.

    Args:
        file_path (str): The path to the file to read.
    """
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return content
    except Exception as e:
        return f"Error reading file '{file_path}': {e}"

def create_directory(directory_path: str) -> str:
    """
    Creates a new directory (folder) at the specified path.

    Args:
        directory_path (str): The path where the directory should be created.
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        return f"Directory '{directory_path}' created successfully."
    except Exception as e:
        return f"Error creating directory '{directory_path}': {e}"