import os

def print_structure(root_dir, indent=0, skip_folders=None):
    if skip_folders is None:
        skip_folders = {"myenv", "__pycache__", ".git", "venv"}

    try:
        items = sorted(os.listdir(root_dir))
    except PermissionError:
        return

    for item in items:
        path = os.path.join(root_dir, item)
        if os.path.isdir(path):
            if item in skip_folders:
                continue
            print('    ' * indent + f"📁 {item}/")
            print_structure(path, indent + 1, skip_folders)
        else:
            print('    ' * indent + f"📄 {item}")

# Example usage
print_structure(r"C:\Users\zzeba\OneDrive\Desktop\GenAI_Intern_Assignment\Project")
