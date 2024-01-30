echo "Starting discord bot"
title palworldbot

cd C:\Users\adric\PycharmProjects\discord_bots\
start /B python3 -m steamcmd_bots.save_game_backup Palworld C:\etc\default\palworldbot.json PalServer-Win64
python3 -m palworldbot.palworldbot