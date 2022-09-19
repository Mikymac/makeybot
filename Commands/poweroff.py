import discord
from discord.ext import commands

@commands.command()
async def example(ctx):
	if(admin in ctx.author.roles) == int(ctx.author.id):
		await audit(f'{ctx.author.display_name} has Powered me down. I will need to be powered on again manually.')
		await bot.logout()
	else:
		await audit(f'')



def setup(bot):
	bot.add_command(example)

#async def example(ctx):
#	await ctx.send("TEST")
