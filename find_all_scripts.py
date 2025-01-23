import os

def print_repo_structure_and_code(root_dir=".", exclude_dirs=None, exclude_files=None):
    """
    Prints the directory structure of the repo along with the content of Python files.

    Args:
        root_dir (str): The root directory to start scanning. Defaults to the current directory.
        exclude_dirs (list): List of directories to exclude from scanning.
        exclude_files (list): List of files to exclude from scanning.
    """
    if exclude_dirs is None:
        exclude_dirs = ["venv", "__pycache__"] 
    if exclude_files is None:
        exclude_files = [os.path.basename(__file__)]  

    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]

        indent_level = dirpath.count(os.sep)
        print("  " * indent_level + f"[{os.path.basename(dirpath)}]")

        for filename in filenames:
            if filename in exclude_files:
                continue

            filepath = os.path.join(dirpath, filename)
            if filename.endswith(".py"):
                print("  " * (indent_level + 1) + f"- {filename}")
                try:
                    with open(filepath, "r") as file:
                        print("  " * (indent_level + 2) + "[Code Start]")
                        for line in file:
                            print("  " * (indent_level + 2) + line.rstrip())
                        print("  " * (indent_level + 2) + "[Code End]")
                except Exception as e:
                    print("  " * (indent_level + 2) + f"[Error reading file: {e}]")
            else:
                print("  " * (indent_level + 1) + f"- {filename}")

if __name__ == "__main__":
    print("Repository Structure and Code:\n")
    print_repo_structure_and_code(exclude_dirs=["venv", "__pycache__"])
