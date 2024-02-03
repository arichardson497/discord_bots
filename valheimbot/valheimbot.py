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
        '!status - Displays if the bot thinks the server is running',
        '!mod_list - Displays list of mods on the server.'
    ]
    MOD_DIRECTORY = 'C:/Games/Mods/Valheim/'
    ZIP_DIRECTORY = 'C:/Games/Zip/Valheim/'
    MOD_JSON = 'C:/Games/Mods/Valheim/required.json'

    def __init__(self):
        super(ValheimBot, self).__init__()

    def get_config_file_location(self):
        return '/etc/default/valheimbot.json'

    def get_install(self):
        return 'C:\steamcmd\steamcmd +login anonymous +force_install_dir valheimdedicatedserver +app_update 896660 validate +quit'

    def get_help_text(self):
        return ValheimBot.HELP_TEXT

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

    async def mod_list(self, message):

        if os.path.exists(ValheimBot.MOD_JSON):
            required = self.read_json_file(ValheimBot.MOD_JSON)

            mod_list = '# Required\n```'
            mods = ''
            for v in required['required']:
                mods += v + '\n'
            mod_list += mods.strip() + '```'

            mod_list += '\n# Optional\n```'
            mods = ''
            for v in required['optional']:
                mods += v + '\n'
            mod_list += mods.strip() + '```'
            await self.send_message(message, mod_list)
        else:
            mods = []
            if os.path.exists(ValheimBot.MOD_DIRECTORY):
                for dir_name in os.listdir(ValheimBot.MOD_DIRECTORY):
                    if os.path.isdir(os.path.join(ValheimBot.MOD_DIRECTORY, dir_name)):
                        mods.append(dir_name)
            mod_list = ''
            for mod in mods:
                mod_list += mod + '\n'
            mod_list = mod_list.strip()
            await self.send_message(message, '```' + mod_list + '```')

    async def get_mods(self, message):
        await self.send_message(message, 'Download the mods here: https://drive.google.com/drive/folders/1--x_eCVlfHWrOj5_f-89dyP68kv6IAxg?usp=drive_link')

    async def stop(self, message, direct_command="True"):
        returnval = subprocess.call(['C:/Program Files/AutoHotkey/v2/AutoHotkey64.exe', 'C:/steamcmd/valheimdedicatedserver/stop_server.ahk'])
        if returnval == 1:
            self.__is_running = False
            await self.send_message(message, 'Server has been stopped successfully.')
        else:
            await self.send_message(message, 'Failed to stop server. I don\'t know what happened.')



if __name__ == '__main__':

    schedule_thread = threading.Thread(target=lambda: scheduled_restart('06:00'))
    schedule_thread.start()

    bot = ValheimBot()
    import steamcmd_bots.run_bot
