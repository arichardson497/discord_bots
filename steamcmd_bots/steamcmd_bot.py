import os
import subprocess
import urllib.request
from abc import abstractmethod
from subprocess import CREATE_NEW_CONSOLE
import discord

from steamcmd_bots.running_bot_single import RunningBotSingle

external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')

print(external_ip)


class SteamCmdBot:

    def __init__(self):
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
    def get_task(self):
        pass

    def get_task_with_exe(self):
        return self.get_task() + '.exe'

    @abstractmethod
    def get_start_process(self):
        pass

    @abstractmethod
    def get_token(self):
        pass

    @abstractmethod
    def get_help_text(self):
        pass

    async def handle_command(self, message):
        split = message.content.split(' ')
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
                self.__is_running = True
                if 'False' not in direct_command:
                     await self.send_message(message, 'Server is up!')
            except Exception as e:
                await self.send_message(message, 'Failed to start server: ' + str(e))
                self.__is_running = False

    async def stop(self, message, direct_command="True"):
        os.system('taskkill /f /im ' + self.get_task_with_exe())
        self.__is_running = False
        if direct_command:
            await self.send_message(message, 'Server has been stopped.')

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
        external_ip = urllib.request.urlopen('https://v4.ident.me').read().decode('utf8')
        await self.send_message(message, external_ip)

    async def send_message(self, msg, message, file=None):
        if len(message) > 1800:
            if message.endswith('```'):
                message = message[:1800] + '```'
            else:
                message = message[:1800]
        if file is None:
            await msg.channel.send(message)
        else:
            await msg.channel.send(message, file=discord.File(file))

