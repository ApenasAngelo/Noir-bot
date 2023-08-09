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


class Database(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot


    @commands.command()
    async def configmusic(self, ctx, music_channel:dc.TextChannel=None):

        auxiliar = Auxiliar(self.bot)
        if ctx.author.guild_permissions.administrator:

            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='guilds'")
            table_exists = cursor.fetchone() is not None

            if not table_exists: 
                self.initialize_database()

            cursor.execute(f"SELECT guild_id FROM guilds WHERE guild_id = {ctx.guild.id}")
            guild_exists = cursor.fetchone() is not None

            if not guild_exists:
                cursor.execute('INSERT INTO guilds (name, guild_id) VALUES (?, ?)', (ctx.guild.name, ctx.guild.id))
                conn.commit()

            self.insert_music_channel_id(music_channel)
            await auxiliar.send_embed_message(ctx, f'O canal de música foi definido para {music_channel.mention}.')

        else:
            await auxiliar.send_embed_message(ctx, 'Você não tem permissão para isso!')


    def initialize_database(self):

        cursor.execute('''CREATE TABLE guilds
                (name TEXT NOT NULL,
                guild_id INTEGER NOT NULL,
                music_channel_id INTEGER)''')
        conn.commit()
            

    def insert_music_channel_id(self, channel):
        
        cursor.execute('UPDATE guilds SET music_channel_id = ? WHERE guild_id = ?', (channel.id, channel.guild.id))
        conn.commit()


    def read_music_channel_id(self, guild):
        
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='guilds'")
        table_exists = cursor.fetchone() is not None
                
        if not table_exists: 
            self.initialize_database()

        cursor.execute(f"SELECT guild_id FROM guilds WHERE guild_id = {guild.id}")
        guild_exists = cursor.fetchone() is not None

        if not guild_exists:
            cursor.execute('INSERT INTO guilds (name, guild_id) VALUES (?, ?)', (guild.name, guild.id))
            conn.commit()

        cursor.execute('SELECT music_channel_id FROM guilds WHERE guild_id = ?', (guild.id,))
        music_channel_id = cursor.fetchone()
        
        if music_channel_id is None:
            return None
        
        return music_channel_id[0]


async def setup(bot):
    await bot.add_cog(Database(bot))