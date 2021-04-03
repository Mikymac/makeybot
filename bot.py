import RPi.GPIO as GPIO
import discord
from discord.ext import commands, tasks
import asyncio
import json
import git
import os
import sys
import random

with open("config.json") as conf:
	data = json.load(conf)

#TEST numero dos

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(21, GPIO.OUT)
GPIO.setup(16, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.output(21, False)
GPIO.output(16, False)
GPIO.output(26, False)

TOKEN = data["TOKEN"]

intents = discord.Intents.default()
intents.members = True
#intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)


on = False
curDoor = False
doorOpen = False
enabled = True

def restart_program():
	python = sys.executable
	os.execl(python, python, * sys.argv)

@bot.command()
@commands.is_owner()
async def update(ctx):
	await audit("I have initiated an Update, please await the online command.")
	await ctx.message.delete()
	repo = git.Repo('/home/pi/makeybot/')
	print("Pre pull")
	repo.git.pull()
	print("Post Pull")
	restart_program()

@bot.command()
@commands.is_owner()
async def restart(ctx):
	await audit("I have initiated a restart, please await the online command.")
	await ctx.message.delete()
	restart_program()

@bot.command()
@commands.is_owner()
async def idcall(ctx, *, test: discord.TextChannel):
	chanID = test.id
	await ctx.send(f"Here's the channel ID for {test}: {chanID}")
	await ctx.message.delete()

@bot.command()
async def send(ctx, channel: discord.TextChannel, *, arg):
	admin = discord.utils.find(lambda r: r.name == "Admin",ctx.guild.roles)
	if(admin in ctx.author.roles or mod in ctx.author.roles ):
		await ctx.message.delete()
		await audit(f'{ctx.author.display_name} used the send command to say "{arg}" in channel: {channel}')
		await channel.send(arg)
		print(arg)
	else:
		await audit(f'{ctx.author.display_name} attempted to use the send command.')

@bot.command()
async def purge(ctx, channel: discord.TextChannel):
	#await bot.get_channel(int(data["whosinID"])).purge()
	admin = discord.utils.find(lambda r: r.name == "Admin",ctx.guild.roles)
	if(admin in ctx.author.roles or mod in ctx.author.roles ):
		await channel.purge()
		await audit(f'{ctx.message.author.display_name} has purged {channel.name}')

@bot.command()
async def disable(ctx):
	global enabled
	enabled = False
	await audit(f'{ctx.message.author.display_name} has disabled automation')
	

@bot.command()
async def enable(ctx):
	global enabled
	enabled = True
	await audit(f'{ctx.message.author.display_name} has enabled automation')

@bot.command()
async def ping(ctx):
	await ctx.send('polo')
	print ('pong')

@bot.command()
async def marco(ctx):
	await ctx.send('pong')
	print ('polo')

@bot.command()
@commands.is_owner()
async def here(ctx):
	await ctx.send(f'{ctx.message.author} is at the space')
	await ctx.message.delete()

@bot.command()
async def open(ctx):
	keyholder = discord.utils.find(lambda r: r.name == "Keyholder",ctx.guild.roles)
	if(keyholder in ctx.author.roles or mod in ctx.author.roles ):
		openings= bot.get_channel(int(data["openingsID"]))
		await openings.send("The Unit is Open <:make:777970381285490688>")
		await audit(f'{ctx.author.display_name} Has used the open command. Automation has been disabled')
		await openings.edit(name="🟢-makerspace-open")
		on = True
		GPIO.output(21, True)
		await ctx.message.delete()
		global enabled
		enabled = false
		

@bot.command()
async def closed(ctx):
	keyholder = discord.utils.find(lambda r: r.name == "Keyholder",ctx.guild.roles)
	if(keyholder in ctx.author.roles or mod in ctx.author.roles ):
		openings= bot.get_channel(int(data["openingsID"]))
		openings.send("The Unit is Closed <:make:777970381285490688>")
		await audit(f'{ctx.author.display_name} Has used the close command. Automation has been disabled')
		on = False
		GPIO.output(21, False)
		await openings.edit(name="🔴-makerspace-closed")
		await ctx.message.delete()
		global enabled
		enabled = false
		
@bot.command()
async def free(ctx, *, item):
	rand = random.randint(0,99)
	print(rand)
	await audit(f'The number rolled was: {rand}')
	if(rand <= 10):
		await ctx.send(f'Here you go {ctx.author.display_name} 1 free {item}')
	else:
		await ctx.send(f"I'm sorry {ctx.author.display_name}, {item} is not free. You must purchase your own." )

@bot.command()
@commands.is_owner()
async def opentest(ctx):
	global curDoor
	await ctx.send("Test")
	await ctx.send(curDoor)

async def task():
	global on
	global curDoor
	global doorOpen
	
	openings = bot.get_channel(int(data["openingsID"]))
	while True:
		if(enabled):
			if (GPIO.input(20) == 0):
				doorOpen = True
			else:
				doorOpen = False

			if(doorOpen != curDoor):
				curDoor = doorOpen
				if(curDoor == True):
					print("Open")
					await bot.get_channel(int(data["openingsID"])).purge()
					await openings.send("The Unit is Open <:make:777970381285490688>")
					await openings.edit(name="🟢-makerspace-open")
				else:
					print("Closed")
					await bot.get_channel(int(data["openingsID"])).purge()
					await openings.send("The Unit is Closed <:make:777970381285490688>")
					await openings.edit(name="🔴-makerspace-closed")

		await asyncio.sleep(60)


async def audit(message):	
	await bot.get_channel(int(data["auditID"])).send(message)

@bot.event
async def on_member_join(member):
	print("Test")
	await bot.get_channel(int(data["introID"])).send(f"Welcome {member.mention} to the MAKEGosport Discord. When you have a moment please read throgh the welcome-and-rules channel. I'm sure everyone will welcome you to the space in due course.")

@bot.event
async def on_ready():
	print ("Ready To Go")
	await audit("*Beep Beep* MakeyBot OnLine")
	curDoor = True
	doorOpen = True
	bot.loop.create_task(task())

bot.run(TOKEN)
