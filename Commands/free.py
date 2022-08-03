from discord.ext import commands
import random

@commands.command()
async def free(ctx, *, item):
        rand = random.randint(0,99)
        print(rand)
        #await audit(f'The number rolled was: {rand}')
        if(rand <= 10):
                await ctx.send(f'Here you go {ctx.author.display_name} 1 free {item}')
        else:
                await ctx.send(f"I'm sorry {ctx.author.display_name}, {item} is not free. You must purchase your own." )


def setup(bot):
	bot.add_command(free)
