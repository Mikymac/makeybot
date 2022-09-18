import RPi.GPIO as GPIO
import discord
from discord.ext import commands, tasks
import asyncio
import json
import git
import os
import sys
import random
import aiofiles

with open("config.json", "r+") as conf:
	data = json.load(conf)
	try:
		conf.seek(0)
		with open("toAppend.txt", "r+") as appen:
			content = appen.readlines()
			newdict = {content[0].strip('\n'): content[1].strip('\n')}
			os.remove("toAppend.txt")
			data.update(newdict)
			json.dump(data, conf, ensure_ascii=False, indent=4)
			print("Updated local config")
	except:
		conf.seek(0)


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

TOKEN = data["TOKEN"]

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

on = False
curDoor = False
doorOpen = False
enabled = True

keyholder = None
mod = None
admin = None

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

bot.load_extension("Commands.ping")

@bot.command()
async def restart(ctx):
	if(admin in ctx.author.roles or mod in ctx.author.roles ):
		await audit("I have initiated a restart, please await the online command.")
		await ctx.message.delete()
		restart_program()

#bot.load_extension("Commands.poweroff")

@bot.command()
async def poweroff(ctx):
	if(admin in ctx.author.roles or int(data["debugID"]) == int(ctx.author.id)):
		await audit(f'{ctx.author.display_name} has Powered me Down. I will need to be powered on again manually.')
		await bot.logout()
	else:
		await audit(f'')

@bot.command()
async def setcode(ctx, code):
	if(admin in ctx.author.roles or mod in ctx.author.roles):
		async with aiofiles.open("code.txt", "a+") as codefile:
			await codefile.truncate(0)
			await codefile.write(code)
			await audit(f'{ctx.author.display_name} has set the code to {code}')
			await ctx.message.delete()
	else:
		await audit(f'{ctx.author.display_name} has attempted to set the code.')

@bot.command()
async def code(ctx):
	if(keyholder in ctx.author.roles):
		async with aiofiles.open("code.txt", "r") as codefile:
			await bot.get_channel(int(data["keyID"])).send(f'The door code is {await codefile.read()}.')
			await ctx.message.delete()
	await audit(f'{ctx.author.display_name} has attempted to receive the code. {bot.get_channel(int(data["rulesID"])).mention}')

@bot.command()
async def appendconfig(ctx, id, *, entry):
	if(int(data["debugID"]) == ctx.author.id):	
		async with aiofiles.open("toAppend.txt", "a+") as appenfile:
			await appenfile.writelines(id + "\n")
			await appenfile.writelines(entry)
		restart_program()
	else:
		await ctx.channel.send(f'User {ctx.author.display_name} is not the Debug User')

@bot.command()
@commands.is_owner()
async def idcall(ctx, *, test: discord.TextChannel):
	chanID = test.id
	await ctx.send(f"Here's the channel ID for {test}: {chanID}")
	await ctx.message.delete()

@bot.command()
async def send(ctx, channel: discord.TextChannel, *, arg):
	if(admin in ctx.author.roles or mod in ctx.author.roles ):
		await ctx.message.delete()
		await audit(f'{ctx.author.display_name} used the send command to say "{arg}" in channel: {channel}')
		await channel.send(arg)
		print(arg)
	else:
		await audit(f'{ctx.author.display_name} attempted to use the send command.')

@bot.command()
async def purge(ctx):
	if(admin in ctx.author.roles or mod in ctx.author.roles ):
		await ctx.message.delete()
		await ctx.channel.purge()
		await audit(f'{ctx.message.author.display_name} has purged {ctx.channel.name}')
	else:
		await audit(f'{ctx.message.author.display_name} attempted to purge {ctx.channel.name}')

@bot.command()
async def disable(ctx):
	if(admin in ctx.author.roles or mod in ctx.author.roles ):
		global enabled
		enabled = False

		await ctx.message.delete()
		await audit(f'{ctx.message.author.display_name} has disabled automation')

@bot.command()
async def enable(ctx):
	if(admin in ctx.author.roles or mod in ctx.author.roles ):
		global enabled
		enabled = True
		global curDoor
		global doorOpen

		curDoor = not doorOpen
		await ctx.message.delete()
		await audit(f'{ctx.message.author.display_name} has enabled automation')

bot.load_extension("Commands.marco")

@bot.command()
@commands.is_owner()
async def here(ctx):
	await ctx.send(f'{ctx.message.author} is at the space')
	await ctx.message.delete()

@bot.command()
async def open(ctx):
	if(keyholder in ctx.author.roles):
		openings= bot.get_channel(int(data["openingsID"]))
		await bot.get_channel(int(data["openingsID"])).purge()
		await openings.send("The Unit is Open <:make:777970381285490688>")
		await audit(f'{ctx.author.display_name} Has used the open command. Automation has been disabled')
		await openings.edit(name="🟢-makerspace-open")
#		on = True
#		GPIO.output(21, True)
		await ctx.message.delete()
		global enabled
		enabled = false

@bot.command()
async def closed(ctx):
	if(keyholder in ctx.author.roles):
		openings= bot.get_channel(int(data["openingsID"]))
		await bot.get_channel(int(data["openingsID"])).purge()
		await openings.send("The Unit is Closed <:make:777970381285490688>")
		await audit(f'{ctx.author.display_name} Has used the close command. Automation has been disabled')
#		on = False
#		GPIO.output(21, False)
		await openings.edit(name="🔴-makerspace-closed")
		await ctx.message.delete()
		global enabled
		enabled = false

bot.load_extension("Commands.free")

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
async def on_message(ctx):
	await bot.process_commands(ctx)
	
	if isinstance(ctx.channel, discord.channel.DMChannel) and ctx.author != bot.user:
		print("The message's content was: ", ctx.content)
		await ctx.channel.send('Thank you for your message, this will be reviewed and replied to within 1-2 days, please be patient.')
		await bot.get_channel(int(data["askadminID"])).send(str(ctx.author.id) + " : " + ctx.author.name + " :  " + ctx.content)
	if ctx.reference is not None and ctx.author.id == 220696408171347968:
		
		id = ctx.reference.message_id
		channel = ctx.channel
		usermessageID = await channel.fetch_message(id)
		userID = str(usermessageID.content).split(" : ")
		try:
			#await channel.send(userID[0])
			user = await bot.fetch_user(userID[0])
			await user.send(ctx.content)
			await channel.send("Messsage sent successfully")
		except:
			await channel.send("ID Not applicable")
@bot.event
async def on_member_join(member):
	await bot.get_channel(int(data["introID"])).send(f"Welcome {member.mention} to the MAKEGosport Discord. When you have a moment please read throgh the welcome-and-rules channel. I'm sure everyone will welcome you to the space in due course.")

@bot.event
async def on_ready():
	print ("Ready To Go")
	await audit("*Beep Beep* MakeyBot OnLine")
	
	if (GPIO.input(20) == 0):
		doorOpen = True
	else:
		doorOpen = False
	curDoor = not doorOpen
	
	global keyholder
	global admin
	global mod
	
	for guild in bot.guilds:
		print(guild.name)
		keyholder = discord.utils.find(lambda r: r.name == "Keyholder", guild.roles)
		admin = discord.utils.find(lambda r: r.name == "Admin", guild.roles)
		mod = discord.utils.find(lambda r: r.name == "Moderator", guild.roles)

	bot.loop.create_task(task())

bot.run(TOKEN)
