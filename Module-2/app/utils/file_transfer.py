import os
import shutil


# ----------------------------------
# COPY FILE
# ----------------------------------

def copy_file(
    source: str,
    destination_folder: str
):

    os.makedirs(
        destination_folder,
        exist_ok=True
    )

    destination = os.path.join(
        destination_folder,
        os.path.basename(source)
    )

    shutil.copy2(
        source,
        destination
    )

    return destination


# ----------------------------------
# CLEAR FOLDER
# ----------------------------------

def clear_folder(
    folder_path: str
):

    if not os.path.exists(
        folder_path
    ):
        return

    for item in os.listdir(
        folder_path
    ):

        item_path = os.path.join(
            folder_path,
            item
        )

        if os.path.isfile(
            item_path
        ):

            os.remove(
                item_path
            )

        elif os.path.isdir(
            item_path
        ):

            shutil.rmtree(
                item_path
            )