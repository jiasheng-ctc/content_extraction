import os

def print_repo_structure(root_dir=".", exclude_dirs=None, exclude_files=None):
    """
    Prints the directory structure of the repo, excluding non-essential files and directories.

    Args:
        root_dir (str): The root directory to start scanning. Defaults to the current directory.
        exclude_dirs (list): List of directories to exclude from scanning.
        exclude_files (list): List of files to exclude from scanning.
    """
    if exclude_dirs is None:
        exclude_dirs = ["venv", "__pycache__", ".git", "hooks", "logs", "branches", "objects", "refs", ".idea"]   
    if exclude_files is None:
        exclude_files = [
            os.path.basename(__file__),  
            ".gitignore",
            "LICENSE",
            "README.md",
            "config.yml",
            "requirements.txt",
        ]

    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]

        indent_level = dirpath.count(os.sep)
        print("  " * indent_level + f"[{os.path.basename(dirpath)}]")

        for filename in filenames:
            if filename in exclude_files or filename.startswith("."):
                continue 

            print("  " * (indent_level + 1) + f"- {filename}")

if __name__ == "__main__":
    print("Repository Structure:\n")
    print_repo_structure(exclude_dirs=["venv", "__pycache__", ".git", "hooks", "logs", "branches", "objects", "refs"])
