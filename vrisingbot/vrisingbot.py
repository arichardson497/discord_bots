import os
import threading
from steamcmd_bots.steamcmd_bot import SteamCmdBot
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECT_DIRECTORY = 'C:/Users/adric/PycharmProjects/discord_bots/'
sys.path.append(PROJECT_DIRECTORY)

from steamcmd_bots.steamcmd_scheduler import scheduled_restart


class VrisingBot(SteamCmdBot):

    def __init__(self):
        super(VrisingBot, self).__init__()

    def get_config_file_location(self):
        return '/etc/default/vrisingbot.json'

    def get_install(self):
        return 'C:\steamcmd\steamcmd.exe +login anonymous +force_install_dir +app_update 1829350 validate +quit'

    def get_stop_ahk_location(self):
        return 'C:/steamcmd/steamapps/common/VRisingDedicatedServer/stop_server.ahk'


if __name__ == '__main__':
    schedule_thread = threading.Thread(target=lambda: scheduled_restart('06:00'))
    schedule_thread.start()

    bot = VrisingBot()
    import steamcmd_bots.run_bot
