import discord
import os
import requests
import tempfile

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
api_url = "https://goggles.magico13.net/api/extract/text"
token = os.environ.get('DISCORD_TOKEN')
# permissions = 274877942784

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Check if the message mentions the bot user
    if client.user in message.mentions:
        if message.attachments:
            for attachment in message.attachments:
                try:
                    # Download the file from the attachment URL
                    file_data = await attachment.read()

                    # Send the file data to the API endpoint
                    response = requests.post(
                        api_url,
                        files={"file": (attachment.filename, file_data)},
                        #verify=False # Disable SSL verification (required for self-signed certificates)
                    )

                    if response.status_code == 200:
                        # Get the json response and pull out the "text" property
                        response_text = response.json()["text"]
                        # Check the length of the response text
                        if len(response_text) <= 2000:
                            # If the response text is less than 2000 characters, send it as a message
                            await message.reply(response_text)
                        else:
                            # If the response text is greater than 2000 characters, save it as a file and send it as an attachment with a message
                            with tempfile.NamedTemporaryFile(mode="w+b", delete=True) as f:
                                f.write(response_text.encode("utf-8"))
                                f.seek(0)
                                basename, _ = os.path.splitext(attachment.filename)
                                new_filename = f"{basename}.txt"
                                await message.reply(content="The response text is too long to send as a message. Here is the text as an attachment:", file=discord.File(f.file, filename=new_filename))
                    else:
                        # If the API endpoint returns an error, send the error message
                        await message.reply("There was an error sending the file to the Goggles API. "+response.text)
                except Exception as e:
                    # If there is an error, send the error message
                    # Also print the exception to the console
                    print(e)
                    await message.reply("There was an error sending the file to the Goggles API. "+str(e))
        else:
            # If the message doesn't have an attachment, send a message
            await message.reply("I couldn't find an attachment in your message. Please upload a file as an attachment.")

if token is None:
    print('DISCORD_TOKEN environment variable is not set.')
else:
    client.run(token)

