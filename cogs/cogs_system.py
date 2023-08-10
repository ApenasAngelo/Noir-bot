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
from cogs.cogs_database import Database
from cogs.cogs_auxiliar import Auxiliar


class System(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot


    @commands.Cog.listener()
    async def on_guild_join(self, guild):

        auxiliar = Auxiliar(self.bot)
        await auxiliar.send_embed_message(guild.system_channel, "Olá, eu sou o Noir! Obrigado por me adicionar ao seu servidor. Digite `-help` para ver meus comandos. Espero que goste de mim! <3")
        await auxiliar.send_embed_message(guild.system_channel, "Digite `-configmusic` para configurar canal aonde são enviadas as músicas tocando.")

        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='guilds'")
        table_exists = cursor.fetchone() is not None
        
        if not table_exists: 
            database = Database(self.bot)
            database.initialize_database()
        
        cursor.execute('INSERT INTO guilds VALUES (?, ?)', (guild.name, guild.id))
        conn.commit()


    @commands.Cog.listener()
    async def on_guild_remove(self, guild):

        cursor.execute('DELETE FROM guilds WHERE guild_id = ?', (guild.id,))
        conn.commit()


    @commands.command()
    async def botoff(self, ctx):

        auxiliar = Auxiliar(self.bot)
        if str(ctx.author.id) == os.getenv('MyUserID'):
            await auxiliar.send_embed_message(ctx, 'Bot encerrando...')
            conn.close()
            await self.bot.close()
        else:
            await auxiliar.send_embed_message(ctx, 'Você não tem permissão para isso!')


    @commands.command()
    async def reloadcogs(self, ctx):

        auxiliar = Auxiliar(self.bot)
        for cog in self.bot.cogs:
            self.bot.reload_extension(f'cogs.cogs_{cog.lower()}')
            print(f"Reloaded Cog: {cog}")
        await auxiliar.send_embed_message(ctx, 'Cogs recarregadas.')


async def setup(bot):
    await bot.add_cog(System(bot))