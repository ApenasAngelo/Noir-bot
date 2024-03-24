import datetime
import re

import discord as dc
from discord.ext import commands

import wavelink as wl


class Auxiliar(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @staticmethod
    async def send_embed_message(
        ctx, message: str = None, deletetime: float = None
    ) -> None:

        msg_embed = dc.Embed(description=message, color=000000)
        await ctx.send(embed=msg_embed, delete_after=deletetime)


async def setup(bot):

    await bot.add_cog(Auxiliar(bot))
