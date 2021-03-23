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
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.output(21, False)
GPIO.output(16, False)
GPIO.output(26, False)

TOKEN = data["TOKEN"]

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!')


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
async def idcall(ctx, *, test: discord.TextChannel):
	chanID = test.id
	await ctx.send(f"Here's the channel ID for {test}: {chanID}")
	await ctx.message.delete()

@bot.command()
async def send(ctx, channel: discord.TextChannel, *, arg):
	role = discord.utils.find(lambda r: r.name == "Admin",ctx.guild.roles)
	if(role in ctx.author.roles or ctx.message.author.id == 220696408171347968):
		await ctx.message.delete()
		await audit(f'{ctx.author.display_name} used the send command to say "{arg}" in channel: {channel}')
		await channel.send(arg)
		print(arg)
	else:
		await audit(f'{ctx.author.display_name} attempted to use the send command.')

@bot.command()
async def purge(ctx):
	await bot.get_channel(821487484071444490).purge()
	await bot.get_channel(822257199438888960).send(f'{ctx.message.author.display_name} has purged channel')

@bot.command()
async def ping(ctx):
	await ctx.send('polo')
#	channel = bot.get_channel(787078050679488512)
#	await channel.edit(name="TestName")
	print ('pong')

@bot.command()
@commands.is_owner()
async def here(ctx):
	await ctx.send(f'{ctx.message.author} is at the space')
	await ctx.message.delete()

@bot.command()
@commands.is_owner()
async def on(ctx):
	openings= bot.get_channel(821487484071444490)
	await ctx.send('On')
	await openings.edit(name="Open")
	on = True
	GPIO.output(21, True)
	await ctx.message.delete()


@bot.command()
@commands.is_owner()
async def off(ctx):
	openings= bot.get_channel(821487484071444490)
	await ctx.send('Off')
	on = False
	GPIO.output(21, False)
	await openings.edit(name="Closed")
	await ctx.message.delete()

@bot.command()
async def freebeer(ctx):
	if(ctx.message.author.id == 220696408171347968 or ctx.message.author.id == 754070539001397408):
		await ctx.send(f'Here you go {ctx.author.display_name}, 2 free cheesecakes')
	else:
		await ctx.send(f"I'm sorry {ctx.author.display_name}, beer is not free. You must purchase your own.")

		
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
	
	openings= bot.get_channel(821487484071444490)
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

async def led_update():
	global on
	openings= bot.get_channel(787078050679488512)

	if(on == True):
		GPIO.output(21, True)
		GPIO.output(16, False)
		on = False
		await openings.edit(name="Open")
	else:
		GPIO.output(21, False)
		GPIO.output(16, True)
		on = True
		await openings.edit(name="Closed")

async def audit(message):	
	await bot.get_channel(822257199438888960).send(message)

@bot.event
async def on_member_join(member):
	await bot.get_channel(754054010792575180).send(f"Welcome to the MakeGosport Discord server {member.display_name}, feel free to introduce yourself and what are your interests. Firstly, Hi I'm MakeyBot. I'm here to help out around the server automating whats possible to automate, nice to meet you.")

@bot.event
async def on_ready():
	print ("Ready To Go")
	await audit("*Beep Beep* MakeyBot OnLine")
	curDoor = True
	doorOpen = True
	bot.loop.create_task(task())

bot.run(TOKEN)


