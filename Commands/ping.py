from discord.ext import commands


@commands.command()
async def ping(ctx):
	await ctx.send('pong')
	print('pong')

def setup(bot):
	bot.add_command(ping)
