import os
from steamcmd_bots.steamcmd_bot import SteamCmdBot
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECT_DIRECTORY = 'C:/Users/adric/PycharmProjects/discord_bots/'
sys.path.append(PROJECT_DIRECTORY)


class EnshroudedBot(SteamCmdBot):

    def __init__(self):
        super(EnshroudedBot, self).__init__()

    def get_config_file_location(self):
        return '/etc/default/enshroudedbot.json'

    def get_install(self):
        return 'C:\steamcmd\steamcmd.exe +login anonymous +app_update 2278520 +quit'

    def get_stop_ahk_location(self):
        return 'C:/Users/adric/PycharmProjects/discord_bots/enshroudedbot/stop_enshrouded_server.ahk'


if __name__ == '__main__':
    bot = EnshroudedBot()
    import steamcmd_bots.run_bot
