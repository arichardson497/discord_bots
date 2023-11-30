import os
import subprocess
import time
from subprocess import Popen, CREATE_NEW_CONSOLE
import threading
from steamcmd_bots.steamcmd_bot import SteamCmdBot

from steamcmd_bots.steamcmd_scheduler import scheduled_restart

class ValheimBot(SteamCmdBot):

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
        super(ValheimBot, self).__init__()


    def get_config_file_location(self):
        return '/etc/default/valheimbot.json'

    def get_install(self):
        return 'C:\steamcmd\steamcmd +login anonymous +force_install_dir valheimdedicatedserver +app_update 896660 validate +quit'

    def get_help_text(self):
        return ValheimBot.HELP_TEXT

    async def address(self, message):
        await self.send_message(message, 'Not Yet Implemented!')

    async def restart_via_schedule(self, message):
        returnval = subprocess.call(['C:/Program Files/AutoHotkey/v2/AutoHotkey64.exe', 'C:/steamcmd/valheimdedicatedserver/stop_server.ahk'])
        if returnval == 1:
            self.__is_running = False
        else:
            print('Failed to restart server')
            return
        time.sleep(10) # JUst make sure things are calmed down

        self.server = subprocess.Popen([self.get_start_process(), '-log'], creationflags=CREATE_NEW_CONSOLE)
        self.__is_running = True
        await self.send_message(message, 'Restart successful!')

    async def update(self, message):
        await self.send_message(message, 'Attempting update....this may take a moment.')
        try:
            await self.stop(message, direct_command="False")
            os.system('C:\steamcmd\steamcmd +login anonymous +force_install_dir valheimdedicatedserver +app_update 896660 validate +quit')
            await self.start(message, direct_command="False")
            await self.send_message(message, 'Update Completed! Server should be up (or will be shortly)')
        except Exception as e:
            await self.send_message(message, 'Error when updating: ' + str(e))

    async def stop(self, message, direct_command="True"):
        returnval = subprocess.call(['C:/Program Files/AutoHotkey/v2/AutoHotkey64.exe', 'C:/steamcmd/valheimdedicatedserver/stop_server.ahk'])
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

    schedule_thread = threading.Thread(target=lambda: scheduled_restart('06:00'))
    schedule_thread.start()

    bot = ValheimBot()
    import steamcmd_bots.run_bot
