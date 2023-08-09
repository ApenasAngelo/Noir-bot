import os
import datetime
from dotenv import load_dotenv

import discord as dc
from discord.ext import commands
from discord.utils import get

import wavelink as wl
from wavelink.ext import spotify

import sqlite3


from globals import guild_queue_list, conn, cursor
from cogs.cogs_auxiliar import Auxiliar


class Misc(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command()
    async def love(self, ctx):

        auxiliar = Auxiliar(self.bot)
        await auxiliar.send_embed_message(ctx, 'Eu te amo! <3')


    @commands.command(aliases = ['limpar', 'clear'])
    async def purge(self, ctx, limit:int=10):

        auxiliar = Auxiliar(self.bot)
        if ctx.author.guild_permissions.administrator:
            if limit < 1:
                await auxiliar.send_embed_message(ctx, 'Digite um valor válido de mensagens para apagar.')
                return

            deleted = await ctx.channel.purge(limit=(limit+1))
            if limit == 1:
                await auxiliar.send_embed_message(ctx, f"{len(deleted)-1} mensagem foi deletada.", 3)
            else:
                await auxiliar.send_embed_message(ctx, f"{len(deleted)-1} mensagens foram deletadas.", 3)


async def setup(bot):
    await bot.add_cog(Misc(bot))