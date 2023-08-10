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


class Music(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot


    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload):

        auxiliar = Auxiliar(self.bot)
        vc: wl.Player = payload.player

        if not vc.queue.loop:
            database = Database(self.bot)
            channel_id = database.read_music_channel_id(vc.guild)
            music_channel = self.bot.get_channel(channel_id)
            
            np_embed = auxiliar.create_np_embed(vc.guild)
            await music_channel.send(embed=np_embed)


    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload):

        vc: wl.Player = payload.player
        track = payload.track

        if vc.queue.loop:
            return await vc.play(track)
        
        guild_queue_list[f'{vc.guild.id}'].pop(0)

        if len(vc.queue) > 0:
            track = vc.queue.get()
            await vc.play(track)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if after.channel is None and member==self.bot.user:
            guild_queue_list[f'{before.channel.guild.id}'].clear()

            print("Bot has been Disconnected")


    @commands.command(aliases = ['p'])
    async def play(self, ctx, *, search:str=None):

        auxiliar = Auxiliar(self.bot)
        database = Database(self.bot)
        if search is None:
            await auxiliar.send_embed_message(ctx, 'Digite o nome de uma música, link do Youtube ou o link do Spotify.')
            return

        channel_id = database.read_music_channel_id(ctx.guild)
        if channel_id is None:
            await auxiliar.send_embed_message(ctx, 'O canal de música não foi configurado. Digite `-configmusic` para configurar.')
            return

        if ctx.author.voice is None:
            await auxiliar.send_embed_message(ctx, 'Você não está em um canal de voz!')
            return

        if ctx.voice_client is None:
            channel = ctx.author.voice.channel
            vc: wl.Player = await channel.connect(cls=wl.Player)

        elif ctx.voice_client.channel.id == ctx.author.voice.channel.id:
            vc: wl.Player = ctx.voice_client

        elif ctx.voice_client.channel.id != ctx.author.voice.channel.id:
            await auxiliar.send_embed_message(ctx, 'O bot já está sendo utilizado em outro canal.')
            return

        track = await auxiliar.process_song_search(ctx, search)
        if not track:
            return

        if isinstance(track, wl.tracks.YouTubePlaylist):
            await ctx.send (type(track))
            if f'{ctx.guild.id}' not in guild_queue_list:
                guild_queue_list[f'{ctx.guild.id}'] = []

            for song in track.tracks:
                info = auxiliar.get_music_info(song)
                guild_queue_list[f'{ctx.guild.id}'].append(info)
                vc.queue.put(song)

            addqueue_embed = auxiliar.create_addqueue_pl_embed(track.name, len(track.tracks), ctx.message.author)
            await ctx.send(embed=addqueue_embed)

        elif isinstance(track, tuple):
            if track[0] == 'album':
                await ctx.send (type(track))
                if f'{ctx.guild.id}' not in guild_queue_list:
                    guild_queue_list[f'{ctx.guild.id}'] = []

                for song in track[1]:
                    info = auxiliar.get_music_info(song)
                    guild_queue_list[f'{ctx.guild.id}'].append(info)
                    vc.queue.put(song)

                addqueue_embed = auxiliar.create_addqueue_spotify_album_embed(track[1][0].album, len(track[1]), ctx.message.author)
                await ctx.send(embed=addqueue_embed)

            elif track[0] == 'playlist':
                await ctx.send (type(track))
                if f'{ctx.guild.id}' not in guild_queue_list:
                    guild_queue_list[f'{ctx.guild.id}'] = []

                for song in track[1]:
                    info = auxiliar.get_music_info(song)
                    guild_queue_list[f'{ctx.guild.id}'].append(info)
                    vc.queue.put(song)

                addqueue_embed = auxiliar.create_addqueue_pl_embed(track[1][0].album, len(track[1]), ctx.message.author)
                await ctx.send(embed=addqueue_embed)


        else:
            await ctx.send (type(track))
            info = auxiliar.get_music_info(track)

            if f'{ctx.guild.id}' not in guild_queue_list:
                guild_queue_list[f'{ctx.guild.id}'] = []

            guild_queue_list[f'{ctx.guild.id}'].append(info)

            addqueue_embed = auxiliar.create_addqueue_embed(info, ctx.message.author)
            await ctx.send(embed=addqueue_embed)

            vc.queue.put(track)

        if not vc.is_playing():
            await vc.play(vc.queue.get())


    @commands.command()
    async def join(self, ctx):

        auxiliar = Auxiliar(self.bot)
        if ctx.author.voice is None:
            await auxiliar.send_embed_message(ctx, 'Você não está em um canal de voz!')
            return None

        if ctx.voice_client is None:
            channel = ctx.author.voice.channel
            wl.Player = await channel.connect(cls=wl.Player)

        elif ctx.voice_client.channel.id != ctx.author.voice.channel.id:
            await auxiliar.send_embed_message(ctx, 'O bot já está sendo utilizado.')
            return None
        
        else:
            await auxiliar.send_embed_message(ctx, 'O bot já está no seu canal de voz.')


    @commands.command()
    async def disconnect(self, ctx):

        auxiliar = Auxiliar(self.bot)
        if ctx.author.voice is None:
            await auxiliar.send_embed_message(ctx, 'Você não está em um canal de voz!')
            return None
        
        if ctx.voice_client is None:
            await auxiliar.send_embed_message(ctx, 'O bot não está em um canal de voz!')
            return None
        
        elif ctx.voice_client.channel.id != ctx.author.voice.channel.id:
            await auxiliar.send_embed_message(ctx, 'Você não pode desconectar o bot em outro canal de voz.')
            return None
        
        vc: wl.Player = ctx.voice_client
        await vc.disconnect()


    @commands.command()
    async def stop(self, ctx):

        auxiliar = Auxiliar(self.bot)
        if ctx.author.voice is None:
            await auxiliar.send_embed_message(ctx, 'Você não está em um canal de voz!')
            return None
        
        if ctx.voice_client is None:
            await auxiliar.send_embed_message(ctx, 'O bot não está em um canal de voz!')
            return None
        
        elif ctx.voice_client.channel.id != ctx.author.voice.channel.id:
            await auxiliar.send_embed_message(ctx, 'Você não pode parar a música com o bot em outro canal de voz.')
            return None
        
        vc: wl.Player = ctx.voice_client

        guild_queue_list[f'{ctx.guild.id}'].clear()
        vc.queue.clear()
        await vc.disconnect()
        await auxiliar.send_embed_message(ctx, 'A música parou.')


    @commands.command()
    async def pause(self, ctx):

        auxiliar = Auxiliar(self.bot)
        if ctx.author.voice is None:
            await auxiliar.send_embed_message(ctx, 'Você não está em um canal de voz!')
            return None
        
        if ctx.voice_client is None:
            await auxiliar.send_embed_message(ctx, 'O bot não está em um canal de voz!')
            return None
        
        elif ctx.voice_client.channel.id != ctx.author.voice.channel.id:
            await auxiliar.send_embed_message(ctx, 'Você não pode pausar a música com o bot em outro canal de voz.')
            return None
        
        vc: wl.Player = ctx.voice_client

        if vc.is_playing():
            await vc.pause()
            await auxiliar.send_embed_message(ctx, 'A música foi pausada.')

        else:
            await auxiliar.send_embed_message(ctx, 'Não tem nada tocando...')


    @commands.command()
    async def resume(self, ctx):

        auxiliar = Auxiliar(self.bot)
        if ctx.author.voice is None:
            await auxiliar.send_embed_message(ctx, 'Você não está em um canal de voz!')
            return None
        
        if ctx.voice_client is None:
            await auxiliar.send_embed_message(ctx, 'O bot não está em um canal de voz!')
            return None
        
        elif ctx.voice_client.channel.id != ctx.author.voice.channel.id:
            await auxiliar.send_embed_message(ctx, 'Você não pode resumir a música com o bot em outro canal de voz.')
            return None
        
        vc: wl.Player = ctx.voice_client

        if vc.is_paused():
            await vc.resume()
            await auxiliar.send_embed_message(ctx, 'A música foi resumida.')

        else:
            await auxiliar.send_embed_message(ctx, 'A música não está pausada...')


    @commands.command()
    async def skip(self, ctx):

        auxiliar = Auxiliar(self.bot)
        if ctx.author.voice is None:
            await auxiliar.send_embed_message(ctx, 'Você não está em um canal de voz!')
            return None
        
        if ctx.voice_client is None:
            await auxiliar.send_embed_message(ctx, 'O bot não está em um canal de voz!')
            return None
        
        elif ctx.voice_client.channel.id != ctx.author.voice.channel.id:
            await auxiliar.send_embed_message(ctx, 'Você não pode pular a música com o bot em outro canal de voz.')
        
        vc: wl.Player = ctx.voice_client

        if vc.is_playing():
            await vc.seek(vc.current.length)
        else:
            await auxiliar.send_embed_message(ctx, 'Não tem nada tocando...')


    @commands.command()
    async def seek(self, ctx, time:int):

        auxiliar = Auxiliar(self.bot)
        if ctx.author.voice is None:
            await auxiliar.send_embed_message(ctx, 'Você não está em um canal de voz!')
            return None
        
        if ctx.voice_client is None:
            await auxiliar.send_embed_message(ctx, 'O bot não está em um canal de voz!')
            return None
        
        elif ctx.voice_client.channel.id != ctx.author.voice.channel.id:
            await auxiliar.send_embed_message(ctx, 'Você não pode passar o tempo da música com o bot em outro canal de voz.')

        vc: wl.Player = ctx.voice_client
        await vc.seek(time*1000)


    @commands.command(aliases = ['q'])
    async def queue(self, ctx):

        auxiliar = Auxiliar(self.bot)
        if ctx.voice_client is None:
            await auxiliar.send_embed_message(ctx, 'O bot não está em um canal de voz!')
            return None
        
        if ctx.voice_client is None:
            await auxiliar.send_embed_message(ctx, 'O bot não está em um canal de voz!')
            return None
        
        vc: wl.Player = ctx.voice_client
        
        formatted_queue = ""

        for index, song in enumerate(guild_queue_list[f'{ctx.guild.id}']):
            if index == 0 and vc.is_playing():
                formatted_queue += f"**{index+1} - [{song['title']}]({song['url']}) ({song['duration']}) (Música Atual)**"
            else:
                formatted_queue += f"**{index+1} -** [{song['title']}]({song['url']}) ({song['duration']})"

            if index < len(guild_queue_list[f'{ctx.guild.id}']) - 1:
                formatted_queue += "\n"
            
        embed = dc.Embed(title="Músicas na fila", description=formatted_queue, color=000000, timestamp=datetime.datetime.now())
        await ctx.send(embed=embed)


    @commands.command(aliases = ['rq'])
    async def removequeue(self, ctx, position:int):

        auxiliar = Auxiliar(self.bot)
        if ctx.author.voice is None:
            await auxiliar.send_embed_message(ctx, 'Você não está em um canal de voz!')
            return None
        
        if ctx.voice_client is None:
            await auxiliar.send_embed_message(ctx, 'O bot não está em um canal de voz!')
            return None
        
        elif ctx.voice_client.channel.id != ctx.author.voice.channel.id:
            await auxiliar.send_embed_message(ctx, 'Você não pode passar o tempo da música com o bot em outro canal de voz.')

        if position == 1:
            await auxiliar.send_embed_message(ctx, 'Você não pode remover a música atual. Use `-skip`')
            return
        
        if position < 1 or position > len(guild_queue_list[f'{ctx.guild.id}']):
            await auxiliar.send_embed_message(ctx, 'Digite uma posição válida da fila de reprodução')
            return
        
        vc: wl.Player = ctx.voice_client
        deleted = guild_queue_list[f'{ctx.guild.id}'][position-1]['title']
        guild_queue_list[f'{ctx.guild.id}'].pop(position-1)
        del vc.queue[position-2]

        await auxiliar.send_embed_message(ctx, f"A música **{deleted}** foi removida da fila de reprodução.")


    @commands.command(aliases = ['np'])
    async def nowplaying(self, ctx):

        auxiliar = Auxiliar(self.bot)
        if ctx.voice_client is None:
            await auxiliar.send_embed_message(ctx, 'O bot não está em um canal de voz!')
            return None
        
        vc: wl.Player = ctx.voice_client

        if not vc.is_playing():
            await auxiliar.send_embed_message(ctx, "Não tem nada tocando...")
        else:
            np_embed = auxiliar.create_np_embed(ctx.guild)
            await ctx.send(embed=np_embed)


async def setup(bot):
    await bot.add_cog(Music(bot))