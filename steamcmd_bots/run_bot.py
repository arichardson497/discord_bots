import discord
from steamcmd_bots.running_bot_single import RunningBotSingle

sb = RunningBotSingle.get_instance().get_current_game_bot()
TOKEN = sb.get_token()

bot = RunningBotSingle.get_instance().get_current_bot()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.startswith('!'):
        await sb.handle_command(message)


def send_private_message(msg, message):
    channel = bot.get_channel(602895210921328672)  # replace with channel id of text channel in discord
    if len(message) > 1800:
        if message.endswith('```'):
            message = message[:1800] + '```'
        else:
            message = message[:1800]
    bot.loop.create_task(channel.send(message))

async def send_message(msg, message, file=None):
    if len(message) > 1800:
        if message.endswith('```'):
            message = message[:1800] + '```'
        else:
            message = message[:1800]
    if file is None:
        await msg.channel.send(message)
    else:
        await msg.channel.send(message, file=discord.File(file))

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

    for guild in bot.guilds:
        channel = discord.utils.get(guild.text_channels, name="general")
        if channel is not None:
            print('Connected to: ' + guild.name)
            print('General Channel id: ' + str(channel.id))

try:
    bot.run(TOKEN)
except Exception as e:
    print(str(e))