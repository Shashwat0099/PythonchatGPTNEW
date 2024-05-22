from telethon import TelegramClient, events
from telethon.tl.functions.channels import InviteToChannelRequest
import requests
import re

# Your API ID and hash (Get this from https://my.telegram.org)
api_id = 'YOUR_API_ID'
api_hash = 'YOUR_API_HASH'
bot_token = 'YOUR_BOT_TOKEN'

# Create the bot and client
bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)
client = TelegramClient('client', api_id, api_hash)

# Step 1: Bot asks for phone number
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond("Please provide your phone number for login:")
    async with bot.conversation(event.chat_id) as conv:
        phone_number = await conv.get_response()
        await client.send_code_request(phone_number.text)
        await event.respond("OTP has been sent to your phone. Please provide the OTP:")
        otp = await conv.get_response()
        await client.sign_in(phone=phone_number.text, code=otp.text)

        await event.respond("Login successful! Now fetching members to add to the group...")

        # Step 2: Fetch members from GitHub
        # Updated to use the specific GitHub repository link provided
        response = requests.get('https://raw.githubusercontent.com/ShashwatMishra0099/Members.run/main/members.txt')
        
        if response.status_code == 200:
            members = re.findall(r'@\w+', response.text)

            # Step 3: Add members to the group
            group = await client.get_entity('https://t.me/your_group_link')

            for member in members:
                try:
                    user = await client.get_input_entity(member)
                    await client(InviteToChannelRequest(group, [user]))
                    await event.respond(f"Added {member} to the group.")
                except Exception as e:
                    await event.respond(f"Failed to add {member}: {e}")
        else:
            await event.respond("Failed to fetch members list from GitHub.")

# Start both the bot and client
bot.start()
client.start()
bot.run_until_disconnected()
client.run_until_disconnected()
