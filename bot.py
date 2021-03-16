import RPi.GPIO as GPIO
import discord
from discord.ext import commands, tasks
import asyncio
import json
import git
import os
import sys

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
	await ctx.message.delete()
	repo = git.Repo('./')
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
	#channel = discord.utils.get(ctx.guild.channels, name=args[0])
	await ctx.message.delete()
	await channel.send(arg)
	print(arg)

@bot.command()
async def ping(ctx):
	await ctx.send('pong')
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
	openings= bot.get_channel(787078050679488512)
	await ctx.send('On')
	await openings.edit(name="Open")
	on = True
	GPIO.output(21, True)
	await ctx.message.delete()

@bot.command()
@commands.is_owner()
async def off(ctx):
	openings= bot.get_channel(787078050679488512)
	await ctx.send('Off')
	on = False
	GPIO.output(21, False)
	await openings.edit(name="Closed")
	await ctx.message.delete()

@bot.command()
async def freebeer(ctx):
	print(message.author.id)


async def task():
	global on
	global curDoor
	global doorOpen
	
	openings= bot.get_channel(787078050679488512)
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
				#await openings.send("Open")
				#await openings.edit(name="Open")
			else:
				print("Cloased")
				#await openings.send("Closed")
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

@bot.event
async def on_ready():
	print ("Ready To Go")
	curDoor = True
	doorOpen = True
	bot.loop.create_task(task())

bot.run(TOKEN)


