import datetime
import random
import asyncio
import inspect

import discord as dc
from discord.ext import commands

import wavelink as wl
from wavelink.ext import spotify

from globals import guild_queue_list, last_queue_message, genius
from cogs.cogs_database import Database
from cogs.cogs_auxiliar import Auxiliar


class Music(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.wait_for_tasks = []


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
        if last_queue_message:
            await last_queue_message.clear_reactions()

        if len(vc.queue) > 0:
            track = vc.queue.get()
            await vc.play(track)


    @commands.Cog.listener()
    async def on_voice_state_update(self, member=dc.Member, before=dc.VoiceState, after=dc.VoiceState):

        vc: wl.Player = member.guild.voice_client

        if member==self.bot.user and after.channel is None:
            guild_queue_list[f'{before.channel.guild.id}'].clear()

            print("Queue has been cleared")
        
        elif member is not self.bot.user and before.channel and not after.channel:
            if self.bot.user in before.channel.members and len(before.channel.members) == 1:
                await vc.disconnect()
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
            vc: wl.Player = await channel.connect(cls=wl.Player, self_deaf=True)

        elif ctx.voice_client.channel.id == ctx.author.voice.channel.id:
            vc: wl.Player = ctx.voice_client

        elif ctx.voice_client.channel.id != ctx.author.voice.channel.id:
            await auxiliar.send_embed_message(ctx, 'O bot já está sendo utilizado em outro canal.')
            return

        track = await auxiliar.process_song_search(ctx, search)
        if not track:
            return

        if isinstance(track, wl.tracks.YouTubePlaylist):
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
                if f'{ctx.guild.id}' not in guild_queue_list:
                    guild_queue_list[f'{ctx.guild.id}'] = []

                for song in track[1]:
                    info = auxiliar.get_music_info(song)
                    guild_queue_list[f'{ctx.guild.id}'].append(info)
                    vc.queue.put(song)

                addqueue_embed = auxiliar.create_addqueue_spotify_album_embed(track[1][0].album, len(track[1]), ctx.message.author)
                await ctx.send(embed=addqueue_embed)

            elif track[0] == 'playlist':
                if f'{ctx.guild.id}' not in guild_queue_list:
                    guild_queue_list[f'{ctx.guild.id}'] = []

                for song in track[2]:
                    info = auxiliar.get_music_info(song)
                    guild_queue_list[f'{ctx.guild.id}'].append(info)
                    vc.queue.put(song)

                addqueue_embed = auxiliar.create_addqueue_spotify_pl_embed(track[1], len(track[2]), ctx.message.author)
                await ctx.send(embed=addqueue_embed)

        else:
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
        print("Bot has been Disconnected")
        


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
        print("Bot has been Disconnected")
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
            await auxiliar.send_embed_message(ctx, f'{ctx.author.mention} pulou a música.')
        else:
            await auxiliar.send_embed_message(ctx, 'Não tem nada tocando...')


    @commands.command(aliases=['goto'])
    async def skipto(self, ctx, *, index: int):

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
            for x in range(index-2):
                del vc.queue[0]
                guild_queue_list[f'{ctx.guild.id}'].pop(0)

            await vc.seek(vc.current.length)
            await auxiliar.send_embed_message(ctx, f'{ctx.author.mention} pulou a música.')
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


    @commands.command(aliases=['q'])
    async def queue(self, ctx):

        global last_queue_message
        auxiliar = Auxiliar(self.bot)
        if ctx.voice_client is None:
            await auxiliar.send_embed_message(ctx, 'O bot não está em um canal de voz!')
            return None

        try:
            for coro in self.wait_for_tasks:
                if coro is not None and inspect.isawaitable(coro):
                    coro.cancel()
        except Exception as e :
            print(e)

        vc: wl.Player = ctx.voice_client

        formatted_queue = ""
        queue_list = guild_queue_list[f'{ctx.guild.id}']
        page_size = 15
        page_num = 0
        num_pages = (len(queue_list) + page_size - 1) // page_size

        start_index = page_num * page_size
        end_index = min(start_index + page_size, len(queue_list))
        formatted_queue = ""

        for index, song in enumerate(queue_list[start_index:end_index]):
            if index == 0 and page_num == 0 and vc.is_playing():
                formatted_queue += f"**{start_index+index+1} - [{song['title']}]({song['url']}) ({song['duration']}) (Música Atual)**"
            else:
                formatted_queue += f"**{start_index+index+1} -** [{song['title']}]({song['url']}) ({song['duration']})"

            if index < len(queue_list) - 1:
                formatted_queue += "\n"

            if len(formatted_queue) > 4096:
                formatted_queue = formatted_queue[:4093] + "..."
                break

        embed = dc.Embed(title="Músicas na fila", description=formatted_queue, color=000000, timestamp=datetime.datetime.now())
        embed.set_footer(text=f"Página {page_num+1}/{num_pages}")
        new_queue_message = await ctx.send(embed=embed)

        if last_queue_message is not None:
            await last_queue_message.clear_reactions()

        last_queue_message = new_queue_message

        if num_pages > 1:
            await last_queue_message.add_reaction("⬅️")
            await last_queue_message.add_reaction("➡️")

            def check(reaction, user):
                return user != self.bot.user and str(reaction.emoji) in ["⬅️", "➡️"]

            page_counts = [0] * num_pages

            while True:
                try:
                    loop = asyncio.get_event_loop()
                    task = loop.create_task(self.bot.wait_for('reaction_add', timeout=15.0, check=check))
                    self.wait_for_tasks.append(task)
                    reaction, user = await task
                except asyncio.TimeoutError:
                    await last_queue_message.clear_reactions()
                    break
                else:
                    if str(reaction.emoji) == "⬅️":
                        page_counts[page_num] += 1
                        page_num = max(0, page_num - 1)
                    elif str(reaction.emoji) == "➡️":
                        page_counts[page_num] += 1
                        page_num = min(num_pages - 1, page_num + 1)

                    start_index = page_num * page_size
                    end_index = min(start_index + page_size, len(queue_list))
                    formatted_queue = ""

                    for index, song in enumerate(queue_list[start_index:end_index]):
                        if index == 0 and page_num == 0 and vc.is_playing():
                            formatted_queue += f"**{start_index+index+1} - [{song['title']}]({song['url']}) ({song['duration']}) (Música Atual)**"
                        else:
                            formatted_queue += f"**{start_index+index+1} -** [{song['title']}]({song['url']}) ({song['duration']})"

                        if index < len(queue_list) - 1:
                            formatted_queue += "\n"

                        if len(formatted_queue) > 4096:
                            formatted_queue = formatted_queue[:4093] + "..."
                            break

                    embed.description = formatted_queue
                    embed.set_footer(text=f"Página {page_num+1}/{num_pages}")
                    await last_queue_message.edit(embed=embed)

                    await reaction.remove(user)
                    page_counts[page_num] += 1


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
            np_embed = auxiliar.create_np_embed(ctx.guild, vc.position)
            await ctx.send(embed=np_embed)


    @commands.command(aliases = ['s'])
    async def shuffle(self, ctx):

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
        
        np_song = guild_queue_list[f'{ctx.guild.id}'][0]
        guild_queue_list[f'{ctx.guild.id}'].pop(0)
        random.shuffle(guild_queue_list[f'{ctx.guild.id}'])
        vc.queue.clear()

        for song in guild_queue_list[f'{ctx.guild.id}']:
            vc.queue(song['track'])
        guild_queue_list[f'{ctx.guild.id}'].insert(0, np_song)

        await auxiliar.send_embed_message(ctx, 'A fila de reprodução foi embaralhada.')

    @commands.command(aliases = ['pnext'])
    async def playnext(self, ctx, *, search:str=None):

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
            vc: wl.Player = await channel.connect(cls=wl.Player, self_deaf=True)

        elif ctx.voice_client.channel.id == ctx.author.voice.channel.id:
            vc: wl.Player = ctx.voice_client

        elif ctx.voice_client.channel.id != ctx.author.voice.channel.id:
            await auxiliar.send_embed_message(ctx, 'O bot já está sendo utilizado em outro canal.')
            return

        track = await auxiliar.process_song_search(ctx, search)
        if not track:
            return

        if isinstance(track, wl.tracks.YouTubePlaylist):
            if f'{ctx.guild.id}' not in guild_queue_list:
                guild_queue_list[f'{ctx.guild.id}'] = []

            if len(guild_queue_list[f'{ctx.guild.id}']) in (0, 1) and len(vc.queue) == 0:
                for song in track.tracks:
                    info = auxiliar.get_music_info(song)
                    guild_queue_list[f'{ctx.guild.id}'].append(info)
                    vc.queue.put(song)
            else:
                for song in reversed(track.tracks):
                    info = auxiliar.get_music_info(song)
                    guild_queue_list[f'{ctx.guild.id}'].insert(1, info)
                    vc.queue.put_at_front(song)

            addqueue_embed = auxiliar.create_addqueue_pl_embed(track.name, len(track.tracks), ctx.message.author)
            await ctx.send(embed=addqueue_embed)

        elif isinstance(track, tuple):
            if track[0] == 'album':
                if f'{ctx.guild.id}' not in guild_queue_list:
                    guild_queue_list[f'{ctx.guild.id}'] = []

                if len(guild_queue_list[f'{ctx.guild.id}']) in (0, 1) and len(vc.queue) == 0:
                    for song in track[1]:
                        info = auxiliar.get_music_info(song)
                        guild_queue_list[f'{ctx.guild.id}'].append(info)
                        vc.queue.put(song)
                else:
                    for song in reversed(track[1]):
                        info = auxiliar.get_music_info(song)
                        guild_queue_list[f'{ctx.guild.id}'].insert(1, info)
                        vc.queue.put_at_front(song)

                addqueue_embed = auxiliar.create_addqueue_spotify_album_embed(track[1][0].album, len(track[1]), ctx.message.author)
                await ctx.send(embed=addqueue_embed)

            elif track[0] == 'playlist':
                if f'{ctx.guild.id}' not in guild_queue_list:
                    guild_queue_list[f'{ctx.guild.id}'] = []

                if len(guild_queue_list[f'{ctx.guild.id}']) in (0, 1) and len(vc.queue) == 0:
                    for song in track[2]:
                        info = auxiliar.get_music_info(song)
                        guild_queue_list[f'{ctx.guild.id}'].append(info)
                        vc.queue.put(song)
                else:
                    for song in reversed(track[2]):
                        info = auxiliar.get_music_info(song)
                        guild_queue_list[f'{ctx.guild.id}'].insert(1, info)
                        vc.queue.put_at_front(song)

                addqueue_embed = auxiliar.create_addqueue_spotify_pl_embed(track[1], len(track[2]), ctx.message.author)
                await ctx.send(embed=addqueue_embed)

        else:
            info = auxiliar.get_music_info(track)

            if f'{ctx.guild.id}' not in guild_queue_list:
                guild_queue_list[f'{ctx.guild.id}'] = []

            if len(guild_queue_list[f'{ctx.guild.id}']) in (0, 1) and len(vc.queue) == 0:
                guild_queue_list[f'{ctx.guild.id}'].append(info)
                vc.queue.put(track)
            else:
                guild_queue_list[f'{ctx.guild.id}'].insert(1, info)
                vc.queue.put_at_front(track)

            addqueue_embed = auxiliar.create_addqueue_embed(info, ctx.message.author)
            await ctx.send(embed=addqueue_embed)

        if not vc.is_playing():
            await vc.play(vc.queue.get())


    @commands.command()
    async def lyrics(self, ctx):

        auxiliar = Auxiliar(self.bot)

        if ctx.voice_client is None:
            await auxiliar.send_embed_message(ctx, 'O bot não está em um canal de voz!')
            return None
        
        vc: wl.Player = ctx.voice_client

        if not vc.is_playing():
            await auxiliar.send_embed_message(ctx, "Não tem nada tocando...")
        else:
            if isinstance(guild_queue_list[f'{ctx.guild.id}'][0]['track'], spotify.SpotifyTrack):

                lyrics = genius.search_song(title=guild_queue_list[f'{ctx.guild.id}'][0]['name'],
                                             artist=guild_queue_list[f'{ctx.guild.id}'][0]['artist']).lyrics

                lyrics = auxiliar.clean_lyrics(lyrics)

                await auxiliar.send_embed_lyrics_message(ctx, guild_queue_list[f'{ctx.guild.id}'][0]['title'], lyrics)
            else:
                await auxiliar.send_embed_message(ctx, "No momento apenas músicas do Spotify são compatíveis com essa função.")

async def setup(bot):
    await bot.add_cog(Music(bot))