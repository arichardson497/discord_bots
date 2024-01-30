
import os
import zipfile
import shutil

class ModInstaller:

    def __init__(self, game_mod_directory):
        self.game_mod_directory = game_mod_directory
        self.mod_config = self.load_mod_config()

    def load_mod_config(self):
        mod_config = {}
        if os.path.exists(self.game_mod_directory):
            for mods in os.listdir(self.game_mod_directory):
                mod_name = os.path.basename(mods)
                if mod_name not in mod_config:
                    mod_config[mod_name] = {'files': []}

            for mod_name in mod_config.keys():
                walk_path = os.path.join(self.game_mod_directory, mod_name)
                for root, dirs, files in os.walk(walk_path):
                    for file_name in files:
                        mod_config[mod_name]['files'].append(os.path.join(root, file_name))
        return mod_config


    def backup_save_files(self, save_file_directory, save_file_names=None):
        pass

    def link_mod(self, mod_name, install_path):
        try:
            install_path = os.path.normpath(install_path)
            if not os.path.exists(install_path):
                raise Exception('Game Path not found: ' + install_path)

            mod_directory = os.path.normpath(os.path.join(self.game_mod_directory, mod_name))
            for file in self.mod_config[mod_name]['files']:
                old_file = file
                normalized_path = os.path.normpath(file)
                mod_file_name = normalized_path.replace(mod_directory + '\\', '')
                if '\\' in mod_file_name:
                    mod_file_name = mod_file_name.split('\\', 1)[0]
                    file = os.path.join(self.game_mod_directory, mod_name, mod_file_name)
                destination = os.path.join(install_path, mod_file_name)
                if os.path.exists(destination) and not os.path.islink(destination):
                    destination = os.path.join(install_path, normalized_path.replace(mod_directory + '\\', ''))
                    file = old_file
                self.create_symbolic_link(file, destination)
        except Exception as e:
            print(f"Error linking mod: {e}")


    def install_mod(self, zip_file_path, mod_name, game_path):
        try:
            game_path = os.path.normpath(game_path)
            if not os.path.exists(game_path):
                raise Exception('Game Path not found: ' + game_path)

            if not os.path.exists(os.path.join(self.game_mod_directory, mod_name)):
                # Extract the contents of the zip file
                with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                    zip_ref.extractall(self.game_mod_directory)
                extracted_files = zip_ref.namelist()

            self.load_mod_config()
            print(f"Mod successfully installed in {self.game_mod_directory}")



            '''
            mod_directory = os.path.normpath(os.path.join(self.game_mod_directory, mod_name))
            for file in self.mod_config[mod_name]['files']:
                normalized_path = os.path.normpath(file)
                mod_file_name = normalized_path.replace(mod_directory + '\\', '')
                if '\\' in mod_file_name:
                    mod_file_name = mod_file_name.split('\\', 1)[0]
                    old_file = file
                    file = os.path.join(self.game_mod_directory, mod_name, mod_file_name)
                destination = os.path.join(game_path, mod_file_name)
                if os.path.exists(destination) and not os.path.islink(destination):
                    destination = os.path.join(game_path, normalized_path.replace(mod_directory + '\\', ''))
                    file = old_file


                self.create_symbolic_link(file, destination)
            '''

        except Exception as e:
            print(f"Error installing mod: {e}")

        self.link_mod(mod_name, game_path)


    def create_symbolic_link(self, source_path, destination_link):
        try:
            # Create a symbolic link
            if not os.path.islink(destination_link):

                parent_directory = os.path.dirname(destination_link)

                while not os.path.exists(parent_directory):
                    # If the parent directory doesn't exist, move one level up
                    destination_link = parent_directory
                    parent_directory = os.path.dirname(parent_directory)

                base_name_source = os.path.basename(source_path)
                base_name_dest = os.path.basename(destination_link)

                while base_name_dest != base_name_source:
                    source_path = source_path.replace('\\' + base_name_source, '')
                    base_name_source = os.path.basename(source_path)
                    base_name_dest = os.path.basename(destination_link)
                    print('')

                os.symlink(source_path, destination_link, target_is_directory=os.path.isdir(source_path))
                print(f"Symbolic link created: {source_path} -> {destination_link}")
            else:
                print('Symbolic link already exists.')
        except OSError as e:
            print(f"Error creating symbolic link: {e}")

    def remove_symbolic_links(self, directory):
        for root, dirs, files in os.walk(directory):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                self.unlink(file_path)

            for dir_name in dirs:
                file_path = os.path.join(root, dir_name)
                self.unlink(file_path)

    def unlink(self, file_path):
        # Check if it's a symbolic link
        if os.path.islink(file_path):
            try:
                # Remove the symbolic link
                os.unlink(file_path)
                print(f"Symbolic link removed: {file_path}")
            except OSError as e:
                print(f"Error removing symbolic link: {e}")


def zip_directories(source_folder, output_folder):
    zip_file_paths = []

    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Loop over items in the source folder
    for item in os.listdir(source_folder):
        item_path = os.path.join(source_folder, item)

        # Check if it's a directory
        if os.path.isdir(item_path):
            # Create a zip file for the directory
            zip_filename = f"{item}.zip"
            zip_filepath = os.path.join(output_folder, zip_filename)

            with zipfile.ZipFile(zip_filepath, 'w') as zip_file:
                # Zip the contents of the directory
                for root, dirs, files in os.walk(item_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, item_path)
                        zip_file.write(file_path, arcname=arcname)

            # Add the zip file path to the list
            zip_file_paths.append(zip_filepath)

    return zip_file_paths

if __name__ == "__main__":
    game_mod_directory = 'C:/Games/Mods/Valheim'
    game_directory = 'C:/Program Files (x86)/Steam/steamapps/common/Valheim/'
    mod_manager = ModInstaller(game_mod_directory)
    zip_path = 'C:/Users/adric/Downloads/ValheimRAFT-2630-1-6-12-1704687518.zip'
    mod_name = 'BepInEx'
    zip_directories(game_mod_directory, 'C:/Games/Zip/Valheim/')
    plugin_dir = os.path.join(game_mod_directory, mod_name, mod_name, 'plugins')

    mod_manager.remove_symbolic_links(game_directory)
    mod_manager.remove_symbolic_links(os.path.join(game_mod_directory, mod_name, mod_name, 'plugins'))
    mod_manager.remove_symbolic_links(os.path.join(game_mod_directory, mod_name, mod_name))

    mod_manager.link_mod(mod_name, game_directory)
    mod_manager.link_mod('Jotunn', plugin_dir)
    mod_manager.link_mod('HookGenPatcher', os.path.join(game_mod_directory, mod_name, mod_name))
    mod_manager.link_mod('ValheimRAFT', plugin_dir)
    mod_manager.link_mod('PlanBuild', plugin_dir)
    mod_manager.link_mod('Seasonality', os.path.join(game_mod_directory, mod_name, mod_name))

    mod_manager.link_mod('CraftFromContainers', plugin_dir)
    mod_manager.link_mod('Server Dev Commands', plugin_dir)
    mod_manager.link_mod('PlantEasily', plugin_dir)
    mod_manager.link_mod('WeaponAdditions', plugin_dir)
   # mod_manager.link_mod('World Edit Commands', plugin_dir)


    #mod_manager.link_mod('EpicLoot', plugin_dir)
   # mod_manager.link_mod('MassFarming', plugin_dir)
  #  mod_manager.link_mod('Infinity Hammer', plugin_dir)