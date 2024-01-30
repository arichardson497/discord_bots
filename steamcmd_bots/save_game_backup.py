import json
import os
from datetime import datetime, timedelta
import shutil, errno
import sys
import subprocess
import time


class SaveGameBackup:



    def __init__(self, game, path, task=None):
        self.config = None
        with open(path, 'r') as f:
            self.config = json.load(f)
        self.backup_save_data(game, task)

    def __check_is_running(self, task):
        s = subprocess.check_output('tasklist', shell=True)
        if task in str(s):
            return True
        return False

    def backup_save_data(self, game_name, task):

        task = task or self.config['task']

        if not self.__check_is_running(task):
            return

        if 'save_game_location' in self.config:
            # Get the current date and time
            current_date = datetime.now()

            # Format the date and time as a string (e.g., "2024-01-27_15-45")
            formatted_datetime = current_date.strftime("%Y-%m-%d_%H-%M")

            save_game = self.config['save_game_location']
            if os.path.exists(save_game):

                self.delete_old_folders('C:/Games/backup_saves/' + game_name + '/')
                destination_dir = 'C:/Games/backup_saves/' + game_name + '/' + formatted_datetime + '/'
                if os.path.isdir(save_game):
                    # save entire directory
                    self.copyanything(save_game, destination_dir)
        return None

    def copyanything(self, src, dst):
        try:
            shutil.copytree(src, dst)
        except OSError as exc:  # python >2.5
            if exc.errno in (errno.ENOTDIR, errno.EINVAL):
                shutil.copy(src, dst)
            else:
                raise Exception('Couldnt create backup of save: ' + str(exc))

    def delete_old_folders(self, base_path):
        # Get the current date and time
        current_date = datetime.now()

        # Define the time threshold (1 day)
        threshold = timedelta(days=3)

        # Get a list of folders in the base path
        folders = os.listdir(base_path)

        # Filter out folders with incorrect date format
        valid_folders = [folder for folder in folders if self.is_valid_date_format(folder)]

        # Sort the valid folders based on creation date (oldest to newest)
        sorted_folders = sorted(valid_folders, key=lambda x: datetime.strptime(x, "%Y-%m-%d_%H-%M"))

        # Iterate over sorted folders
        for folder_name in sorted_folders:
            folder_path = os.path.join(base_path, folder_name)

            # Check if the entry is a directory
            if os.path.isdir(folder_path):
                try:
                    # Parse the folder name as a datetime object
                    folder_date = datetime.strptime(folder_name, "%Y-%m-%d_%H-%M")

                    # Check if the folder is older than 1 day
                    if current_date - folder_date > threshold:
                        # Check if there is more than one folder left
                        if len(sorted_folders) > 96:
                            # Delete the folder and its contents
                            shutil.rmtree(folder_path)
                            print(f"Deleted folder: {folder_path}")
                        else:
                            print(f"Skipped deletion for the only remaining folder: {folder_path}")

                except ValueError:
                    # Handle folders with incorrect date format (skip them)
                    print(f"Skipped folder with incorrect date format: {folder_path}")

    def is_valid_date_format(self, folder_name):
        try:
            # Attempt to parse the folder name as a datetime object
            datetime.strptime(folder_name, "%Y-%m-%d_%H-%M")
            return True
        except ValueError:
            return False

if __name__ == "__main__":
    game = sys.argv[1]
    path = sys.argv[2]
    task_override = None
    if len(sys.argv) > 3:
        task_override = sys.argv[3]
    SaveGameBackup(game, path, task=task_override)
    minutes_to_run = [15, 30, 45, 0]
    last_min_ran = -1
    while True:
        time_now = datetime.now()
        current_min = time_now.minute
        if (current_min in minutes_to_run and last_min_ran != current_min):
            SaveGameBackup(game, path, task=task_override)
        else:
            time.sleep(30)


