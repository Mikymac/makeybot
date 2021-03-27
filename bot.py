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
	role = discord.utils.find(lambda r: r.name == "Admin",ctx.guild.roles)
	if(role in ctx.author.roles or ctx.message.author.id == int(data["debugID"])):
		await ctx.message.delete()
		await audit(f'{ctx.author.display_name} used the send command to say "{arg}" in channel: {channel}')
		await channel.send(arg)
		print(arg)
	else:
		await audit(f'{ctx.author.display_name} attempted to use the send command.')

@bot.command()
async def purge(ctx):
	await bot.get_channel(int(data["whosinID"])).purge()
	await audit(f'{ctx.message.author.display_name} has purged channel')

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
		await openings.send('The Unit is currently Open')
		await openings.edit(name="🟢Open")
		on = True
		GPIO.output(21, True)
		await ctx.message.delete()


@bot.command()
async def closed(ctx):
	keyholder = discord.utils.find(lambda r: r.name == "Keyholder",ctx.guild.roles)
	if(keyholder in ctx.author.roles or mod in ctx.author.roles ):
		openings= bot.get_channel(int(data["openingsID"]))
		await openings.send('The Unit is currently Closed')
		on = False
		GPIO.output(21, False)
		await openings.edit(name="⛔Closed")
		await ctx.message.delete()

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
async def setcode(ctx, arg):
	data["code"] = arg	
	with open("config.json") as conf:
		json.load(conf)


@bot.command()
@commands.is_owner()
async def newcode(ctx):
	data["code"] = []
	data["code"].append("1234")
	with open("config.json") as confOut:
		json.dump(data, confOut)

@bot.command()
async def code(ctx):
	print(data["code"])

async def task():
	global on
	global curDoor
	global doorOpen
	
	openings = bot.get_channel(int(data["openingsID"]))
	while True:
		if (GPIO.input(20) == 0):
			doorOpen = True
			#await led_update()
			#GPIO.output(26, True)
			#await asyncio.sleep(3)
			#GPIO.output(26, False)
		else:
			doorOpen = False
					
		if(doorOpen != curDoor):
			curDoor = doorOpen
			if(curDoor == True):
				print("Open")
				await openings.send("Open")
				#await openings.edit(name="Open")
			else:
				print("Cloased")
				await openings.send("Closed")
				#await openings.edit(name="Closed")
					
					
		await asyncio.sleep(.1)

async def sendRegister():
	embedvar = discord.Embed(title="Register", description="Who is present at the space", color=0x00ff00)
	embedvar.add_field(name="Field1", value = "hi", inline=False)
	embedvar.add_field(name="Field2", value = "hi2", inline=False)
	await bot.get_channel(int(data["auditID"])).send(embed=embedvar)
	

#async def led_update():
#	global on
#	openings= bot.get_channel(787078050679488512)
#
#	if(on == True):
#		GPIO.output(21, True)
#		GPIO.output(16, False)
#		on = False
#		await openings.edit(name="Open")
#	else:
#		GPIO.output(21, False)
#		GPIO.output(16, True)
#		on = True
#		await openings.edit(name="Closed")

async def audit(message):	
	await bot.get_channel(int(data["auditID"])).send(message)

@bot.event
async def on_member_join(member):
	print("Test")
	await bot.get_channel(int(data["introID"])).send(f"Welcome to the MakeGosport Discord server {member.mention}, feel free to introduce yourself and what are your interests. Firstly, Hi I'm MakeyBot. I'm here to help out around the server automating whats possible to automate, nice to meet you.")

@bot.event
async def on_ready():
	print ("Ready To Go")
	await audit("*Beep Beep* MakeyBot OnLine")
	curDoor = True
	doorOpen = True
	await sendRegister()
	bot.loop.create_task(task())

bot.run(TOKEN)


