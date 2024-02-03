import os
import subprocess
import pygetwindow as gw
from subprocess import CREATE_NEW_CONSOLE
from steamcmd_bots.steamcmd_bot import SteamCmdBot
import ctypes
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECT_DIRECTORY = 'C:/Users/adric/PycharmProjects/discord_bots/'
sys.path.append(PROJECT_DIRECTORY)


class AdminBot(SteamCmdBot):

    HELP_TEXT = [
        '!start <bot name> - Starts the bot for the associated game',
        '!stop <bot name> - Stops the bot (Note: this force kills the process)',
        '!ip - Gives the IP address of the machine (it may change, cannot be bothered to do static)'
    ]

    def __init__(self):
        super(AdminBot, self).__init__()

    def get_config_file_location(self):
        return '/etc/default/adminbot.json'

    def get_help_text(self):
        return AdminBot.HELP_TEXT


    def check_if_running(self, title):
        try:
            windows = gw.getWindowsWithTitle(title)
            for window in windows:
                if self.is_cmd_window(window):
                    return True
            return False
        except IndexError:
            print(f"Command prompt window with title '{title}' not found.")
            return False
        except Exception as e:
            print(f"Error: {e}")
            return False

    def get_list_of_bots(self):
        files = os.listdir(PROJECT_DIRECTORY)
        bots = []
        for f in files:
            if '.bat' in f and 'adminbot' not in f:
                bots.append(f)
        return bots


    async def start(self, message, *args):
        bot_name = args[0]
        if not bot_name:
            await self.send_message(message, 'A bot name is required.')

        for f in self.get_list_of_bots():
            if bot_name in f:
                title = self.get_title(PROJECT_DIRECTORY + '/' + f)
                if not self.check_if_running(title):
                    subprocess.Popen([PROJECT_DIRECTORY + '/' + f], creationflags=CREATE_NEW_CONSOLE)
                else:
                    await self.send_message(message, 'bot is already running')

    async def stop(self, message, *args):
        bot_name = args[0]
        for f in self.get_list_of_bots():
            if bot_name in f:
                title = self.get_title(PROJECT_DIRECTORY + '/' + f)
                if title and self.check_if_running(title):
                    success = self.kill_command_prompt_by_title(title)
                    if success:
                        await self.send_message(message, title + ' bot stopped.')
                    else:
                        await self.send_message(message, 'Failed to stop: ' + title)
                else:
                    await self.send_message(message, 'Failed to find title of bot.')

    def get_title(self, file_path):
        try:
            lines = []
            with open(file_path, 'r') as file:
                lines = file.readlines()
            for line in lines:
                if 'title' in line:
                    return line.split('title')[-1].strip()

        except FileNotFoundError:
            print(f"Error: Batch file '{file_path}' not found.")
        except Exception as e:
            print(f"Error: {e}")
        return None

if __name__ == '__main__':
    bot = AdminBot()
    import steamcmd_bots.run_bot
