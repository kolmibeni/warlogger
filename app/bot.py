# bot.py
from fileinput import filename
import json
from ntpath import join
import os
import random
import discord
import datetime
from dotenv import load_dotenv

# 1
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_NAME = os.getenv('CHANNEL_NAME')

# 2
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='>', intents=intents)


def get_today_filename():
    todayDate = str(datetime.datetime.now().date())
    filename = todayDate + '_voice.json'
    return filename

# RESPOND TO EVENTS
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    
    filename = get_today_filename()
    
    if not os.path.isfile(filename):
        data = {}
        jsonFile = open(filename, 'w')
        json.dump(data, jsonFile)
        jsonFile.close()
        print(f'Log file does not exist. {filename} has been created.')
    else:
        print(f'Log file exists. Records stored in {filename}')

@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to my Discord server!'
    )

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    brooklyn_99_quotes = [
        'I\'m the human form of the 💯 emoji.',
        'Bingpot!',
        (
            'Cool. Cool cool cool cool cool cool cool, '
            'no doubt no doubt no doubt no doubt.'
        ),
    ]

    if message.content == '99!':
        response = random.choice(brooklyn_99_quotes)
        await message.channel.send(response)
    elif message.content == 'raise-exception':
        raise discord.DiscordException
    
    await bot.process_commands(message)

@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'{datetime.datetime.now()}: {args[0]}\n')
        else:
            raise

@bot.event
# async def on_voice_state_update(self, member:discord.Member, before:discord.VoiceState, after:discord.VoiceState):
async def on_voice_state_update(member:discord.Member, before, after):    
    filename = get_today_filename()
    jsonFile = open(filename, 'r')
    data = json.load(jsonFile)
    jsonFile.close()

    ch_before = str(before.channel)
    ch_after = str(after.channel)
    member_name = str(member.display_name)

    if member_name not in data: #no member record, create new
        print("jancok")
        data[member_name] = {}
        data[member_name]["name"] = member_name
        data[member_name]["join_time"] = {}
        data[member_name]["leave_time"] = {}

    counter_join = len(data[member_name]["join_time"])
    counter_leave = len(data[member_name]["leave_time"])

    if ch_before != CHANNEL_NAME and ch_after == CHANNEL_NAME: #joining channel
        print(f'{datetime.datetime.now()}: {member_name} joined {ch_after}')                
        
        data[member_name]["join_time"][str(counter_join+1)] = str(datetime.datetime.now())
        # print(data[member_name]["join_time"])
        
    elif ch_before == CHANNEL_NAME and ch_after != CHANNEL_NAME: #leaving channel
        print(f'{datetime.datetime.now()}: {member_name} left {ch_before}')

        data[member_name]["leave_time"][str(counter_leave+1)] = str(datetime.datetime.now())
        # print(data)        

    jsonFile = open(filename, 'w')
    json.dump(data, jsonFile)
    jsonFile.close()

        

# RECEIVE COMMAND FROM USERS

@bot.command(name = "absendc", help='Get WOE/WOC Discord attendance list')
async def  generate_absen_discord(ctx):
    jsonFile = open('voice.json', 'r')
    data = json.load(jsonFile)
    jsonFile.close()

    online_members = "Online Members : \n"
    counter = 1

    for member in data.values():
        # print(member["join_time"])
        # 2022-05-05 18:36:53.671941        
        now = datetime.datetime.now()

        if "join_time" in member:
            join_time = datetime.datetime.strptime(member["join_time"], "%Y-%m-%d %H:%M:%S.%f").time()
        else:
            join_time = now.replace(hour=22, minute=00, second=0, microsecond=0).time()

        if "leave_time" in member:
            leave_time = datetime.datetime.strptime(member["leave_time"], "%Y-%m-%d %H:%M:%S.%f").time()
        else:
            leave_time = now.replace(hour=22, minute=00, second=0, microsecond=0).time()
        
        check_in_time = now.replace(hour=21, minute=30, second=0, microsecond=0).time()
        check_out_time = now.replace(hour=22, minute=30, second=0, microsecond=0).time()
        print(join_time)
        if join_time < check_out_time and leave_time > check_out_time:
            print("jancok")
            online_members += f'{str(counter)}. {member["name"]}\n'
            # online_members += f'{str(counter)}. {member["name"]} - [IN={join_time}] - [OUT={leave_time}] \n'
            counter+=1

    # members = '\n - '.join([member.name for member in guild.members])
    # print(f'Guild Members:\n - {members}')
    await ctx.send(online_members)

@bot.command(name='99', help='Responds with a random quote from Brooklyn 99')
async def nine_nine(ctx):
    brooklyn_99_quotes = [
        'I\'m the human form of the 💯 emoji.',
        'Bingpot!',
        (
            'Cool. Cool cool cool cool cool cool cool, '
            'no doubt no doubt no doubt no doubt.'
        ),
    ]

    response = random.choice(brooklyn_99_quotes)
    await ctx.send(response)

@bot.command(name='roll_dice', help='Simulates rolling dice.')
async def roll_dice(ctx, number_of_dice: int, number_of_sides: int):
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))

@bot.command(name='roll', help='Roll random number 1-100.')
async def roll(ctx):
    num = str(random.randint(1, 100))
    
    await ctx.send('You roll '.join(num))


bot.run(TOKEN)
