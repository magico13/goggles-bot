import discord
import os
import requests
import re
import tempfile

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
api_url = "https://goggles.magico13.net/api/extract/text"
token = os.environ.get('DISCORD_TOKEN')
# permissions = 274877942784

async def call_text_extraction_api(filename, filedata):
    response = requests.post(
        api_url,
        files={"file": (filename, filedata)}
    )

    response.raise_for_status()
    return response.json().get("text")

async def process_file(message, filename, filedata):
    try:
        response_text = await call_text_extraction_api(filename, filedata)

        if response_text is None:
            await message.reply("There was an error processing the file. The response did not contain a 'text' field.")
        elif len(response_text) >= 2000:
            with tempfile.NamedTemporaryFile(mode="w+b", delete=True) as f:
                f.write(response_text.encode("utf-8"))
                f.seek(0)
                basename, _ = os.path.splitext(filename)
                new_filename = f"{basename}.txt"
                await message.reply(content="The response text is too long to send as a message. Here is the text as an attachment:", file=discord.File(f.file, filename=new_filename))
        else:
            await message.reply(response_text)
    except Exception as e:
        print(e)
        await message.reply(f"There was an error sending the file to the text extraction API. {str(e)}")

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user or client.user not in message.mentions:
        return
    
    attachments = message.attachments
    attachment_files = []

    for attachment in attachments:
        file_data = await attachment.read()
        attachment_files.append({
            'filename': attachment.filename,
            'filedata': file_data
        })

    link_pattern = re.compile(r'http\S+')
    links = link_pattern.findall(message.content)
    link_files = []

    for link in links:
        try:
            link_data = requests.get(link).content
            link_files.append({
                'filename': link.split('/')[-1],
                'filedata': link_data
            })
        except Exception as e:
            print(e)

    all_files = attachment_files + link_files

    if not all_files:
        await message.reply("I couldn't find an attachment or a link in your message. Please upload a file as an attachment or provide a link.")

    for file in all_files:
        await process_file(message, file['filename'], file['filedata'])

if token is None:
    print('DISCORD_TOKEN environment variable is not set.')
else:
    client.run(token)
