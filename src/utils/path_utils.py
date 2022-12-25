from pathlib import Path

def determine_folder(folder_name, input_folder=None) -> Path:

    if input_folder:
        folder_name = input_folder / folder_name
        check_folder(folder_name)
        return folder_name
    else:
        folder_name = Path().absolute().parent.parent / folder_name  # looking in src directory
        check_folder(folder_name)
        return folder_name


def check_folder(path):

    if path.exists():
        print("exists")
        return
    else:
        path.mkdir(parents=True, exist_ok=True)
        print("making")
        return