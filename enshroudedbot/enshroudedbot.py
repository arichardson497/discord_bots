import os
import subprocess
import time
import urllib
from subprocess import Popen, CREATE_NEW_CONSOLE
import threading
from steamcmd_bots.steamcmd_bot import SteamCmdBot
from os import path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECT_DIRECTORY = 'C:/Users/adric/PycharmProjects/discord_bots/'
sys.path.append(PROJECT_DIRECTORY)

from steamcmd_bots.steamcmd_scheduler import scheduled_restart

class EnshroudedBot(SteamCmdBot):

    HELP_TEXT = [
        '!start - Starts the Server',
        '!stop - Stops the Server (Note: this force kills the process)',
        '!restart - Just calls stop and start....pretty technical stuff',
        '!update - Executes update command and restarts the server',
        '!ip - Gives the IP address of the machine (it may change, cannot be bothered to do static)',
        '!password - Gives the password needed to join the server',
        '!status - Displays if the bot thinks the server is running'
    ]

    def __init__(self):
        super(EnshroudedBot, self).__init__()


    def get_port(self):
        return 0


    def get_config_file_location(self):
        return '/etc/default/enshroudedbot.json'

    def get_install(self):
        return 'C:\steamcmd\steamcmd.exe +login anonymous +app_update 2278520 +quit'

    def get_help_text(self):
        return EnshroudedBot.HELP_TEXT

    async def address(self, message):
        await self.send_message(message, 'Not Yet Implemented!')

    async def ip(self, message):
        external_ip = urllib.request.urlopen('https://v4.ident.me').read().decode('utf8')
        await self.send_message(message, external_ip + ':' + str(self.get_port()))


    async def install(self, message):
        await self.send_message(message, 'Attempting install....this may take a moment.')
        os.system('C:\steamcmd\steamcmd.exe +login anonymous +app_update 2394010 validate +quit')
        try:
            pass
        finally:
            pass

    async def update(self, message):
        await self.send_message(message, 'Attempting update....this may take a moment.')
        try:
            await self.stop(message, direct_command="False")
            os.system(self.get_install())
            await self.start(message, direct_command="False")
            await self.send_message(message, 'Update Completed! Server should be up (or will be shortly)')
        except Exception as e:
            await self.send_message(message, 'Error when updating: ' + str(e))

    async def stop(self, message, direct_command="True"):
        returnval = subprocess.call(['C:/Program Files/AutoHotkey/v2/AutoHotkey64.exe', 'C:/steamcmd/steamapps/common/PalServer/stop_server.ahk'])
        if returnval == 1:
            self.__is_running = False
            await self.send_message(message, 'Server has been stopped successfully.')
        else:
            await self.send_message(message, 'Failed to stop server. I don\'t know what happened.')

    async def save(self, message):
        await self.send_message(message, 'Save not yet implemented, working on it though!')

    async def password(self, message):
        await self.send_message(message, '4543!')

if __name__ == '__main__':

    bot = EnshroudedBot()
    import steamcmd_bots.run_bot
