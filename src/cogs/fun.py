import random
import re

import discord
from discord.ext import commands


class Fun(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["8ball", "8b", "8"])
    async def _8ball(self, ctx, *, question):
        """The absolute classic 8ball. You cannot have a bot without this function."""
        embed = discord.Embed(title="Q:", description=question)
        embed.add_field(name="<:think4:661236485667946506>", value=random.choice(_8ball_responses))
        await ctx.send(embed=embed)

    @commands.command(aliases=["c"])
    async def choose(self, ctx, *, choices):
        """Picks one of passed choices separated by ";"."""
        result = choices.split(';')
        embed = discord.Embed(title="I choose... <:think6:667672019017400323> ", description=random.choice(result))
        await ctx.send(embed=embed)

    @commands.command()
    async def b(self, ctx, *, text):
        """Converts input into emojified text. Handles simple ascii letters and numbers 0-9."""
        # Make text uppercase
        text = text.upper()
        # Remove everything apart
        regex = re.compile("[^A-Z0-9\\s]")
        text = regex.sub("", text)
        # Create a new string using provided nato alphabet and text
        text = "".join(map(b_dictionary.get, text))
        await ctx.message.delete(delay=None)
        await ctx.send(text)


b_dictionary = {'A': ':regional_indicator_a:',
                'B': ':b:',
                'C': ':regional_indicator_c:',
                'D': ':regional_indicator_d:',
                'E': ':regional_indicator_e:',
                'F': ':regional_indicator_f:',
                'G': ':regional_indicator_g:',
                "H": ":regional_indicator_h:",
                'I': ':regional_indicator_i:',
                'J': ':regional_indicator_j:',
                'K': ':regional_indicator_k:',
                'L': ':regional_indicator_l:',
                'M': ':regional_indicator_m:',
                'N': ':regional_indicator_n:',
                'O': ':regional_indicator_o:',
                'P': ':regional_indicator_p:',
                'Q': ':regional_indicator_q:',
                'R': ':regional_indicator_r:',
                'S': ':regional_indicator_s:',
                'T': ':regional_indicator_t:',
                'U': ':regional_indicator_u:',
                'V': ':regional_indicator_v:',
                'W': ':regional_indicator_w:',
                'X': ':regional_indicator_x:',
                'Y': ':regional_indicator_y:',
                'Z': ':regional_indicator_z:',
                ' ': '<:space:676196986164084736>',  # Custom emoji because discord's blue square is different blue.
                '0': ':zero:',
                '1': ':one:',
                '2': ':two:',
                '3': ':three:',
                '4': ':four:',
                '5': ':five:',
                '6': ':six:',
                '7': ':seven:',
                '8': ':eight:',
                '9': ':nine:',
                }

_8ball_responses = ["Yes!",
                    "No idea bro...",
                    "I do think so.",
                    "Most likely!",
                    "lol not gonna happen.",
                    "Bad news...",
                    "Very doubtful...",
                    "Without a doubt.",
                    "No.",
                    "Nah.."
                    ]


def setup(client):
    client.add_cog(Fun(client))
