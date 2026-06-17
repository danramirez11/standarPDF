import os
import shutil
from datetime import datetime, timedelta

UPLOADS_FOLDER = "uploads"

MAX_AGE_HOURS = 2


def cleanup_old_uploads():

    if not os.path.exists(UPLOADS_FOLDER):
        return

    now = datetime.now()

    max_age = timedelta(
        hours=MAX_AGE_HOURS
    )

    for folder_name in os.listdir(
        UPLOADS_FOLDER
    ):

        folder_path = os.path.join(
            UPLOADS_FOLDER,
            folder_name
        )

        if not os.path.isdir(folder_path):
            continue

        created_time = datetime.fromtimestamp(
            os.path.getctime(folder_path)
        )

        age = now - created_time

        if age > max_age:

            print(
                f"Deleting old session: {folder_name}"
            )

            try:
                shutil.rmtree(folder_path)
            except Exception as e:
                print(
                    f"Error deleting {folder_name}: {e}"
                )