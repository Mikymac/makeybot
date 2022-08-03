from discord.ext import commands

@commands.command()
async def marco(ctx):
        await ctx.send('polo')
        print ('polo')


def setup(bot):
	bot.add_command(marco)
