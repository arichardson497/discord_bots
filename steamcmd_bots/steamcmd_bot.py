import os
import subprocess
import urllib.request
from abc import abstractmethod
from subprocess import CREATE_NEW_CONSOLE
import discord
import time
import threading
import re           # needed to split on space ignoring quotes
import json         # for reading the config file
import zipfile
import shutil, errno
import ctypes
import pygetwindow as gw
import pyautogui
from datetime import datetime

from steamcmd_bots.running_bot_single import RunningBotSingle


class SteamCmdBot:

    DEFAULT_HELP_TEXT = [
        '!start - Starts the Server',
        '!stop - Stops the Server (Note: this force kills the process)',
        '!restart - Just calls stop and start....pretty technical stuff',
        '!update - Executes update command and restarts the server',
        '!ip - Gives the IP address of the machine (it may change, cannot be bothered to do static)',
        '!password - Gives the password needed to join the server',
        '!status - Displays if the bot thinks the server is running'
    ]

    def __init__(self):
        self.config = None
        self.__load_config_file()
        self.__is_running = self.__check_is_running()
        self.server = None
        self.return_id = None
        intents = discord.Intents.default()
        intents.message_content = True

        self.bot = discord.Client(intents=intents)

        RunningBotSingle.get_instance().set_current_game_bot(self)
        RunningBotSingle.get_instance().set_current_bot(self.bot)
        self.schedule_thread = None
        self.schedule_is_running = False
        self.keep_running = False

    def __load_config_file(self):
        with open(self.get_config_file_location(), 'r') as f:
            self.config = json.load(f)

    def keep_running_thread(self):
        while True:
            if not self.__check_is_running() and self.keep_running:
                try:
                    self.server = subprocess.Popen([self.get_start_process(), '-log'], creationflags=CREATE_NEW_CONSOLE)
                except Exception as e:
                    print(str(e))
            time.sleep(60) # wait for 1 minute

    #needs @ event but i'm not sure how to do that right now
    async def on_ready(self):
        t = threading.Thread(target=self.keep_running_thread())
        t.start()

    def __check_is_running(self):
        s = subprocess.check_output('tasklist', shell=True)
        if self.get_task() in str(s):
            return True
        return False

    def is_running(self):
        return self.__is_running

    def set_is_running(self, val):
        self.__is_running = val


    @abstractmethod
    def get_install(self):
        return None

    @abstractmethod
    def get_config_file_location(self):
        pass

    @abstractmethod
    def get_task(self):
        return self.config['task']

    def get_task_with_exe(self):
        return self.get_task() + '.exe' if '.exe' not in self.get_task() else self.get_task()

    @abstractmethod
    def get_start_process(self):
        return self.config['start_process']

    @abstractmethod
    def get_token(self):
        return self.config['token']

    @abstractmethod
    def get_help_text(self):
        return SteamCmdBot.DEFAULT_HELP_TEXT

    @abstractmethod
    def get_port(self):
        return self.config['port']

    @abstractmethod
    def get_password(self):
        return self.config['password']

    @abstractmethod
    def get_stop_ahk_location(self):
        return 'C:/User/adrich/PycharmProjects/discord_bots/steamcmd_bots/stop_server.ahk'

    def read_json_file(self, json_file_path):
        json_info = {}
        with open(json_file_path, 'r') as fp:
            json_info = json.load(fp)
        return json_info

    def zip_directories(self, source_folder, output_folder):
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

    def delete_directory_contents(self, directory_path):
        try:
            # Ensure the directory exists
            if os.path.exists(directory_path):
                # Delete the contents of the directory
                for item in os.listdir(directory_path):
                    item_path = os.path.join(directory_path, item)

                    if os.path.isfile(item_path):
                        os.remove(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)

                print(f"Contents of '{directory_path}' deleted successfully.")
            else:
                print(f"Directory '{directory_path}' does not exist.")
        except Exception as e:
            print(f"Error deleting contents: {e}")



    async def handle_command(self, message):

        pattern = re.compile(r'[^\s"]+|"[^"]*"')
        split = pattern.findall(message.content)
        args = split[1:]
        args.insert(0, message)
        command = split[0].replace('!', '')
        if hasattr(self, command):
            try:
                await eval('self.' + command)(*args)
            except Exception as e:
                await self.send_message(message, str(e))
        else:
            await self.send_message(message, 'Command: ' + split[0] + ' is not supported.')

    async def install(self, message):
        await self.send_message(message, 'Attempting install....this may take a moment.')
        try:
            os.system(str(self.get_install()))
        except Exception as e:
            await self.send_message(message, 'Failed install: ' + str(e))


    async def status(self, message):
        if self.__check_is_running():
            await self.send_message(message, 'Server is running!')
        else:
            await self.send_message(message, 'Server is not running.')


    async def start(self, message, direct_command='True'):
        if not self.__check_is_running():
            if 'False' not in direct_command:
                await self.send_message(message, 'Attempting to start server....')
            try:
                self.server = subprocess.Popen([self.get_start_process(), '-log'], creationflags=CREATE_NEW_CONSOLE)
                self.keep_running = True
                if 'False' not in direct_command:
                     await self.send_message(message, 'Server is up!')
            except Exception as e:
                await self.send_message(message, 'Failed to start server: ' + str(e))
                self.keep_running = False

    async def update(self, message):
        await self.send_message(message, 'Attempting update....this may take a moment.')
        try:
            await self.stop(message, direct_command="False")
            os.system(str(self.get_install()))
            await self.start(message, direct_command="False")
            await self.send_message(message, 'Update Completed! Server should be up (or will be shortly)')
        except Exception as e:
            await self.send_message(message, 'Error when updating: ' + str(e))

    @abstractmethod
    async def stop(self, message, *args):

        success = self.kill_command_prompt_by_title(self.get_task())
        if success:
            await self.send_message(message, 'Server has been stopped.')
            return

        '''
        ahk_script = self.get_stop_ahk_location()
        if ahk_script:
            await self.stop_via_ahk(message, ahk_script)
        else:
            os.system('taskkill /f /im ' + self.get_task_with_exe())
            self.keep_running = False
            if direct_command:
                await self.send_message(message, 'Server has been stopped.')
        '''

    def get_window_class_name(self, window):
        class_name_buffer = ctypes.create_unicode_buffer(256)
        ctypes.windll.user32.GetClassNameW(window._hWnd, class_name_buffer, ctypes.sizeof(class_name_buffer))
        return class_name_buffer.value

    def is_cmd_window(self, window):
        class_name = self.get_window_class_name(window)
        return "ConsoleWindowClass" in class_name


    def kill_command_prompt_by_title(self, title):
        try:
            cmd_window = None
            for window in gw.getWindowsWithTitle(title):
                if self.is_cmd_window(window):
                    cmd_window = window
                    break
            if not cmd_window:
                return
            cmd_window.activate()
            # Send Ctrl+C
            self.__close_window(cmd_window, 'ctrl', 'c')
            time.sleep(5)
            self.__close_window(cmd_window, 'ctrl', 'c')
            time.sleep(1)
            self.__close_window(cmd_window, 'ctrl', 'c')
            time.sleep(1)
            self.__close_window(cmd_window, 'Y')
            time.sleep(1)
            self.__close_window(cmd_window, 'enter')

            print(f"Ctrl+C sent to the command prompt window with title '{title}'.")
            return True
        except IndexError:
            print(f"Error: Command prompt window with title '{title}' not found.")
        except Exception as e:
            print(f"Error: {e}")
        return False

    def __close_window(self, cmd_window, *args):
        if cmd_window.isActive():
            pyautogui.hotkey(args)

    async def password(self, message):
        try:
            password = self.get_password()
            await self.send_message(message, "```" + password + "```")
        except Exception as e:
            await self.send_message(message, 'No password is set for this game.')

    async def stop_via_ahk(self, message, ahk_script):
        returnval = subprocess.call(['C:/Program Files/AutoHotkey/v2/AutoHotkey64.exe', ahk_script])
        if returnval == 1:
            self.__is_running = False
            await self.send_message(message, 'Server has been stopped successfully.')
        else:
            await self.send_message(message, 'Failed to stop server. I don\'t know what happened.')

    async def restart(self, message):
        await self.stop(message)
        await self.start(message)

    async def help(self, message):

        help_text = ''

        for line in self.get_help_text():
            help_text += line + '\n'
        await self.send_message(message, '```' + help_text + '```')

    async def mark(self, message):
        await self.send_message(message, 'The Worst...')

    async def ip(self, message):
        port = ''
        try:
            port = str(self.get_port())
        except:
            port = 'None'

        external_ip = urllib.request.urlopen('https://v4.ident.me').read().decode('utf8')
        await self.send_message(message, external_ip + ':' + port)


    async def send_message(self, msg, message, file=None):
        if len(message) > 1800:
            if message.endswith('```'):
                message = message[:1800] + '```'
            else:
                message = message[:1800]
        if file is None:
            await msg.channel.send(message)
        elif isinstance(file, list):
            fs = [discord.File(f) for f in file]
            await msg.channel.send(message, files=fs)
        else:
            await msg.channel.send(message, file=discord.File(file))

