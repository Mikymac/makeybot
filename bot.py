import RPi.GPIO as GPIO
import discord
from discord.ext import commands, tasks
import asyncio

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(21, GPIO.OUT)
GPIO.setup(16, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.output(21, False)
GPIO.output(16, False)
GPIO.output(26, False)


bot = commands.Bot(command_prefix='!')

on = False
curDoor = False
doorOpen = False

@bot.command()
async def ping(ctx):
	await ctx.send('pong')
#	channel = bot.get_channel(787078050679488512)
#	await channel.edit(name="TestName")
	print ('pong')

@bot.command()
async def here(ctx):
	await ctx.send(f'{ctx.message.author} is at the space')

@bot.command()
async def on(ctx):
	openings= bot.get_channel(787078050679488512)
	await ctx.send('On')
	await openings.edit(name="Open")
	on = True
	GPIO.output(21, True)

@bot.command()
async def off(ctx):
	openings= bot.get_channel(787078050679488512)
	await ctx.send('Off')
	on = False
	GPIO.output(21, False)
	await openings.edit(name="Closed")

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
				await openings.send("Open")
				#await openings.edit(name="Open")
			else:
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

@bot.event
async def on_ready():
	print ("Ready To Go")
	curDoor = False
	doorOpen = False
	bot.loop.create_task(task())

bot.run(TOKEN)


