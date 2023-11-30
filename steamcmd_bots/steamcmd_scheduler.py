import requests
import schedule
import time

def send_command(command, webhook_url):
    payload = {"content": command}
    requests.post(webhook_url, json=payload)

def scheduled_restart(restart_time):
    webhook_url = "https://discord.com/api/webhooks/1072950010272043068/9N7Jo7zzGEPn5pwmUcjOZSZ4ip2u_W_6DEvHVg6d8YGtPiWKyuUvHun0bVk2OnE64qKW"
    #schedule.every().day.at(restart_time).do(lambda: send_command('!restart_via_schedule', webhook_url=webhook_url))
    while True:
     #   schedule.run_pending()
        time.sleep(1)
        break
