import asyncio
import collections

import discord
import os
import subprocess, signal
import threading

from discord.ext import tasks, commands
import time
from datetime import datetime

GUILD = "unpleasant_company"

from collections import OrderedDict

from steamcmd_bots.steamcmd_bot import SteamCmdBot

class SatisfactorBot(SteamCmdBot):

    HELP_TEXT = [
        '!start - Starts the Server',
        '!stop - Stops the Server (Note: this force kills the process)',
        '!restart - Just calls stop and start....pretty technical stuff',
        '!update - Executes update command and restarts the server',
        '!ip - Gives the IP address of the machine (it may change, cannot be bothered to do static)',
        '!status - Displays if the bot thinks the server is running',
        '!upload_blueprint - Attach files with this message and it will upload the blueprints to the server',
        '!get_blueprint \"BLUEPRINT NAME\" - Supply the name of the blueprint (no extension) in quotes to get saved blueprints',
        '!list_blueprints - Lists all blueprints on the server.'
    ]

    def __init__(self):
        super(SatisfactorBot, self).__init__()

    def get_config_file_location(self):
        return '/etc/default/satisfactorbot.json'

    def get_help_text(self):
        return SatisfactorBot.HELP_TEXT

    def get_blueprint_directory(self):
        return self.config['blueprint_location']

    async def update(self, message):
        await self.send_message(message, 'Attempting update....this may take a moment.')
        try:
            await self.stop(message, direct_command="False")
            os.system('C:\steamcmd\steamcmd +login anonymous +force_install_dir SatisfactoryDedicatedServer +app_update 1690800 -beta experimental validate +quit')
            await self.start(message, direct_command="False")
            await self.send_message(message, 'Update Completed! Server should be up (or will be shortly)')
        except Exception as e:
            await self.send_message(message, 'Error when updating: ' + str(e))

    async def upload_blueprint(self, message):
        if message.attachments is not None:
            not_all_files = False
            for f in message.attachments:
                blueprint_name = self.get_blueprint_directory() + f.filename
                await f.save(blueprint_name)
                if not os.path.exists(blueprint_name):
                    not_all_files = True

            if not_all_files:
                await self.send_message(message, 'Not all files were saved and I do not know why')
            else:
                await self.send_message(message, 'All blueprints have been saved. A server restart will be needed to see them in game.')

    async def get_blueprint(self, message, blueprint_name):
        blueprint_name = blueprint_name.replace('"', '')
        files = [self.get_blueprint_directory() + blueprint_name + '.sbp', self.get_blueprint_directory() + blueprint_name + '.sbpcfg']
        if all([True if os.path.exists(x) else False for x in files]):
            await self.send_message(message, 'Here ya go : ', file=files)
        else:
            await self.send_message(message, 'I couldn\'t find that file')

    async def list_blueprints(self, message):
        blueprints = set()
        for file in os.listdir(self.get_blueprint_directory()):
            if file.endswith('sbp'):
                bp_name = file.split('.')[0]
                blueprints.add(bp_name)
        blueprint_str = ''
        for x in blueprints:
            blueprint_str += x + '\n'
        await self.send_message(message, '```' + blueprint_str + '```')

    async def save_file(self, message):
        SAVE_GAME_LOCATION = self.config['save_game_location'] #'C:\\Users\\adric\\AppData\\Local\\FactoryGame\\Saved\\SaveGames\\server'
        save_games = []
        most_recent_file_timestamp = 0
        most_recent_file = None
        for file in os.listdir(SAVE_GAME_LOCATION):
            if file.endswith('sav') and 'CALCULATOR' not in file:
                file_timestamp = os.path.getmtime(SAVE_GAME_LOCATION + '\\' + file)
                if file_timestamp > most_recent_file_timestamp:
                    most_recent_file_timestamp = file_timestamp
                    most_recent_file = file
        await self.send_message(message, 'Most recent file is : ' + most_recent_file, file=SAVE_GAME_LOCATION + '\\' + most_recent_file)

    def watch(self):
        fp = open('C:\steamcmd\satisfactorydedicatedserver\FactoryGame\Saved\Logs\FactoryGame.log', 'r')
        words = ['Join succeeded']
        while True:
            new = fp.readline()
            if new:
                for word in words:
                    if word in new:
                        yield (word, new)
            else:
                time.sleep(.5)

    async def last_online(self, message):
        directory = 'C:\steamcmd\satisfactorydedicatedserver\FactoryGame\Saved\Logs'
        time_log = {}
        for file in os.listdir(directory):
            fp = open(directory + '\\' + file, 'r')
            for line in fp.readlines():
                if 'Join succeeded' in line:
                    username = line.split('succeeded:')[1].replace('\n', '')
                    timestr = line.split('][')[0][1:-4]
                    check_time = datetime.strptime(timestr, '%Y.%m.%d-%H.%M.%S')
                    check_time_milis = check_time.timestamp()
                    check_time_milis = check_time_milis - ((60 * 60) * 5)
                    adjusted_time = datetime.fromtimestamp(check_time_milis)
                    if username not in time_log:
                        time_log[username] = adjusted_time
                    else:
                        if adjusted_time > time_log[username]:
                            time_log[username] = adjusted_time
        list_to_be_sorted = []
        for key, value in time_log.items():
            list_to_be_sorted.append({'username': key, 'timestamp': value})
        newlist = sorted(list_to_be_sorted, key=lambda d: d['timestamp'])
        final_message = '```'
        for entry in newlist:
            final_message += entry['timestamp'].strftime("%m/%d/%Y, %H:%M:%S") + ' => ' + entry['username'] + '\n'
        final_message += '```'
        await self.send_message(message, final_message)

    async def check_users(self, message):
        fp = open('C:\steamcmd\satisfactorydedicatedserver\FactoryGame\Saved\Logs\FactoryGame.log', 'r')
        save_lines = []
        for line in fp.readlines():
            if 'Join succeeded' in line:
                save_lines.append(line)
       # self.send_private_message(message, '```' + str(save_lines) + '```')


    async def restart(self, message):
        await self.stop(message)
        await self.start(message)



if __name__ == '__main__':
    bot = SatisfactorBot()
    import steamcmd_bots.run_bot