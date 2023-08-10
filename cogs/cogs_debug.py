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


class Debug(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command()
    async def teste(self, ctx, search):
        if str(ctx.author.id) == os.getenv('MyUserID'):
            tracks= await auxiliar.process_song_search(ctx, search)
            await ctx.send(type(tracks))
        else:
            auxiliar = Auxiliar(self.bot)
            await auxiliar.send_embed_message(ctx, 'Você não tem permissão para isso!')
        


    @commands.command()
    async def tq(self, ctx):
        if str(ctx.author.id) == os.getenv('MyUserID'):
            vc: wl.Player = ctx.voice_client
            await ctx.send(str(vc.queue))
            await ctx.send(len(vc.queue))
        else:
            auxiliar = Auxiliar(self.bot)
            await auxiliar.send_embed_message(ctx, 'Você não tem permissão para isso!')


async def setup(bot):
    await bot.add_cog(Debug(bot))