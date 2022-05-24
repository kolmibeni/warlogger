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


def get_filename_today():
    todayDate = str(datetime.datetime.now().date())
    filename = todayDate + '_voice.json'
    return filename

# RESPOND TO EVENTS
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    
    filename = get_filename_today()
    
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
    filename = get_filename_today()
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
    filename = get_filename_today()
    jsonFile = open(filename, 'r')
    data = json.load(jsonFile)
    jsonFile.close()
    
    now = datetime.datetime.now()
    pretext = "Online Members : \n"
    online_members = ""
    counter_member = 1
    weekday = now.weekday()
    online_members_under = ""
    counter_member_under = 1

    if weekday == 3: #if THURSDAY (WOE)
        online_threshold = float(os.getenv('ONLINE_TIME_WOE'))
    else: #if SUNDAY (WOC)
        online_threshold = float(os.getenv('ONLINE_TIME_WOC'))

    for member in data.values(): # for each member
        # print(member["join_time"]["1"])
        # print(len(member["join_time"]))
        # print(len(member["leave_time"]))
        # 2022-05-05 18:36:53.671941        
        check_in_time = now.replace(hour=21, minute=00, second=0, microsecond=0).time()

        counter_join = 1
        war_duration = 0

        for join in member["join_time"]: # for each join time record in each member
            
            # get join time, should exist by default otherwise said member would have no record at all
            join_time = datetime.datetime.strptime(member["join_time"][str(counter_join)], "%Y-%m-%d %H:%M:%S.%f")
            # print(member["name"])
            # print(join_time)

            # only join_time after check_in_time is counted
            # to filter out join_time that is non-related with WOE/WOC
            if join_time.time() >= check_in_time: 
            # if 1==1:
                if str(counter_join) in member["leave_time"]: # if member has a matching leave time, means already leave the channel
                    leave_time = datetime.datetime.strptime(member["leave_time"][str(counter_join)], "%Y-%m-%d %H:%M:%S.%f")
                else: # if member hasn't leave the channel since last join, then:
                    # assumption 1: leave time is 2300
                    # leave_time = now.replace(hour=23, minute=00, second=0, microsecond=0)

                    # assumption 2: leave time is now, when record is collected
                    leave_time = now 

                # get difference in minutes
                minutes_diff = (leave_time - join_time).total_seconds() / 60.0   

                # accumulate online duration
                war_duration += minutes_diff
                
            # forward counter to the next join record
            counter_join += 1            
        
        # print(war_duration)
        if war_duration >= online_threshold:
        # if 1==1:
            # online_members += f'{str(counter_member)}. {member["name"]} [{round(war_duration,2)}mins]\n'
            online_members += f'{str(counter_member)}. {member["name"]}\n'
            counter_member +=1        
        else:
            online_members_under += f'{str(counter_member_under)}. {member["name"]} [{round(war_duration,2)}mins]\n'
            counter_member_under +=1        
    
    pretext += f"{counter_member-1}/{len(data)}\n"
    subtext = f"\nUnder {online_threshold}mins:\n"
    await ctx.send(pretext + online_members + subtext + online_members_under)

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

@bot.command(name='set_status', help='Set bot status into a predefined activity.')
async def set_status(ctx):
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Dangdut Pantura"))


bot.run(TOKEN)
