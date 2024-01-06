import asyncio
import datetime
import inspect
import random

import discord as dc
import wavelink as wl
from discord.ext import commands

from cogs.cogs_auxiliar import Auxiliar
from cogs.cogs_database import Database


class Music(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.wait_for_tasks = []

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wl.TrackStartEventPayload) -> None:

        database = Database(self.bot)
        
        channel_id = database.read_music_channel_id(payload.player.guild)
        music_channel = self.bot.get_channel(channel_id)

        np_embed = Auxiliar.create_np_embed(payload.track, payload.player.queue)
        await music_channel.send(embed=np_embed)

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wl.TrackEndEventPayload) -> None:
        
        if payload.player:
            if len(payload.player.queue) > 0:
                await payload.player.play(payload.player.queue.get())

    @commands.Cog.listener()
    async def on_voice_state_update(self, member=dc.Member, before=dc.VoiceState, after=dc.VoiceState):

        vc: wl.Player = member.guild.voice_client

        if member == self.bot.user and after.channel is None:
            print("Queue has been cleared")

        elif member is not self.bot.user and before.channel and not after.channel:
            if self.bot.user in before.channel.members and len(before.channel.members) == 1:
                vc.queue.clear()
                await vc.disconnect()
                print("Bot has been Disconnected")

    @commands.command(aliases=['p', 'pyt', 'pnext', 'pytnext'])
    async def play(self, ctx, *, search: str = None) -> None:

        database = Database(self.bot)

        if search is None:
            await Auxiliar.send_embed_message(ctx,  'Digite o nome de uma música, link do Youtube ou o link do Spotify.')
            return

        channel_id = database.read_music_channel_id(ctx.guild)
        if channel_id is None:
            await Auxiliar.send_embed_message(ctx,  'O canal de música não foi configurado. Digite `-configmusic` para '
                                                    'configurar.')
            return

        if ctx.author.voice is None:
            await Auxiliar.send_embed_message(ctx,  'Você não está em um canal de voz!')
            return

        if ctx.voice_client is None:
            channel = ctx.author.voice.channel
            vc: wl.Player = await channel.connect(cls=wl.Player, self_deaf=True)

        elif ctx.voice_client.channel.id == ctx.author.voice.channel.id:
            vc: wl.Player = ctx.voice_client

        else:
            await Auxiliar.send_embed_message(ctx,  'O bot já está sendo utilizado em outro canal.')
            return



        if ctx.invoked_with == 'pyt' or ctx.invoked_with == 'pytnext':
            tracks: wl.Search = await wl.Playable.search(search, source=wl.TrackSource.YouTube)
        else:
            tracks: wl.Search = await wl.Playable.search(search)
        
        if not tracks:
            await ctx.send('Não foi possível adicionar à fila.')
            return

        if isinstance(tracks, wl.Playlist):
            await ctx.send(embed=Auxiliar.create_addqueue_pl_embed(tracks, ctx.message.author))
        else:
            tracks: wl.Playable = tracks[0]
            await ctx.send(embed=Auxiliar.create_addqueue_embed(tracks, ctx.message.author))

        vc.queue.put(tracks)

        if not vc.playing:
            await vc.play(vc.queue.get())

    @commands.command()
    async def join(self, ctx):

        if ctx.author.voice is None:
            await Auxiliar.send_embed_message(ctx, 'Você não está em um canal de voz!')
            return None

        if ctx.voice_client is None:
            channel = ctx.author.voice.channel
            wl.Player = await channel.connect(cls=wl.Player)

        elif ctx.voice_client.channel.id != ctx.author.voice.channel.id:
            await Auxiliar.send_embed_message(ctx, 'O bot já está sendo utilizado.')
            return None

        else:
            await Auxiliar.send_embed_message(ctx, 'O bot já está no seu canal de voz.')

    @commands.command()
    async def disconnect(self, ctx):

        if ctx.author.voice is None:
            await Auxiliar.send_embed_message(ctx, 'Você não está em um canal de voz!')
            return None

        if ctx.voice_client is None:
            await Auxiliar.send_embed_message(ctx, 'O bot não está em um canal de voz!')
            return None

        elif ctx.voice_client.channel.id != ctx.author.voice.channel.id:
            await Auxiliar.send_embed_message(ctx, 'Você não pode desconectar o bot em outro canal de voz.')
            return None

        vc: wl.Player = ctx.voice_client
        await vc.disconnect()
        print("Bot has been Disconnected")

    @commands.command()
    async def stop(self, ctx):

        if ctx.author.voice is None:
            await Auxiliar.send_embed_message(ctx, 'Você não está em um canal de voz!')
            return None

        if ctx.voice_client is None:
            await Auxiliar.send_embed_message(ctx, 'O bot não está em um canal de voz!')
            return None

        elif ctx.voice_client.channel.id != ctx.author.voice.channel.id:
            await Auxiliar.send_embed_message(ctx, 'Você não pode parar a música com o bot em outro canal de voz.')
            return None

        vc: wl.Player = ctx.voice_client

        vc.queue.clear()
        await vc.disconnect()
        await Auxiliar.send_embed_message(ctx, 'A música parou.')

    @commands.command()
    async def pause(self, ctx):

        if ctx.author.voice is None:
            await Auxiliar.send_embed_message(ctx, 'Você não está em um canal de voz!')
            return None

        if ctx.voice_client is None:
            await Auxiliar.send_embed_message(ctx, 'O bot não está em um canal de voz!')
            return None

        elif ctx.voice_client.channel.id != ctx.author.voice.channel.id:
            await Auxiliar.send_embed_message(ctx, 'Você não pode pausar a música com o bot em outro canal de voz.')
            return None

        vc: wl.Player = ctx.voice_client

        if vc.playing:
            if not vc.paused:
                await vc.pause(True)
                await Auxiliar.send_embed_message(ctx, 'A música foi pausada.')
            else:
                await vc.pause(False)
                await Auxiliar.send_embed_message(ctx, 'A música foi despausada.')

        else:
            await Auxiliar.send_embed_message(ctx, 'Não tem nada tocando...')

    @commands.command()
    async def resume(self, ctx):

        if ctx.author.voice is None:
            await Auxiliar.send_embed_message(ctx, 'Você não está em um canal de voz!')
            return None

        if ctx.voice_client is None:
            await Auxiliar.send_embed_message(ctx, 'O bot não está em um canal de voz!')
            return None

        elif ctx.voice_client.channel.id != ctx.author.voice.channel.id:
            await Auxiliar.send_embed_message(ctx, 'Você não pode resumir a música com o bot em outro canal de voz.')
            return None

        vc: wl.Player = ctx.voice_client

        if vc.paused:
            await vc.pause(False)
            await Auxiliar.send_embed_message(ctx, 'A música foi despausada.')

        else:
            await Auxiliar.send_embed_message(ctx, 'A música não está pausada...')

    @commands.command()
    async def skip(self, ctx):

        if ctx.author.voice is None:
            await Auxiliar.send_embed_message(ctx, 'Você não está em um canal de voz!')
            return None

        if ctx.voice_client is None:
            await Auxiliar.send_embed_message(ctx, 'O bot não está em um canal de voz!')
            return None

        elif ctx.voice_client.channel.id != ctx.author.voice.channel.id:
            await Auxiliar.send_embed_message(ctx, 'Você não pode pular a música com o bot em outro canal de voz.')

        vc: wl.Player = ctx.voice_client

        if vc.playing:
            track = await vc.skip()
            await Auxiliar.send_embed_message(ctx, f'a música {track.title} foi pulada por {ctx.author.mention}.')
        else:
            await Auxiliar.send_embed_message(ctx, 'Não tem nada tocando...')

    @commands.command(aliases=['goto'])
    async def skipto(self, ctx, *, index: int):

        if ctx.author.voice is None:
            await Auxiliar.send_embed_message(ctx, 'Você não está em um canal de voz!')
            return None

        if ctx.voice_client is None:
            await Auxiliar.send_embed_message(ctx, 'O bot não está em um canal de voz!')
            return None

        elif ctx.voice_client.channel.id != ctx.author.voice.channel.id:
            await Auxiliar.send_embed_message(ctx, 'Você não pode pular a música com o bot em outro canal de voz.')

        vc: wl.Player = ctx.voice_client

        if vc.playing:
            for x in range(index - 1):
                await vc.queue.delete(0)

            await vc.skip()
            await Auxiliar.send_embed_message(ctx, f'{ctx.author.mention} pulou {index - 1} músicas.')
        else:
            await Auxiliar.send_embed_message(ctx, 'Não tem nada tocando...')

    @commands.command()
    async def seek(self, ctx, time: int):

        if ctx.author.voice is None:
            await Auxiliar.send_embed_message(ctx, 'Você não está em um canal de voz!')
            return None

        if ctx.voice_client is None:
            await Auxiliar.send_embed_message(ctx, 'O bot não está em um canal de voz!')
            return None

        elif ctx.voice_client.channel.id != ctx.author.voice.channel.id:
            await Auxiliar.send_embed_message(ctx, 'Você não pode passar o tempo da música com o bot em outro canal '
                                                   'de voz.')

        vc: wl.Player = ctx.voice_client
        await vc.seek(time * 1000)

    @commands.command(aliases=['q'])
    async def queue(self, ctx):

        if ctx.voice_client is None:
            await Auxiliar.send_embed_message(ctx, 'O bot não está em um canal de voz!')
            return None

        try:
            for coro in self.wait_for_tasks:
                if coro is not None and inspect.isawaitable(coro):
                    coro.cancel()
        except Exception as e:
            print(e)

        vc: wl.Player = ctx.voice_client

        queue_list = vc.queue
        page_size = 15
        page_num = 0
        num_pages = (len(queue_list) + page_size - 1) // page_size

        start_index = page_num * page_size
        end_index = min(start_index + page_size, len(queue_list))
        formatted_queue = ""

        for index, track in enumerate(queue_list[start_index:end_index]):

            if index == 0 and page_num == 0 and vc.playing:
                title = f"{vc.current.author} - {vc.current.title}"
                duration = Auxiliar.format_time(vc.current.length)
                if vc.current.source == "spotify":
                    url = f"https://open.spotify.com/intl-pt/track/{vc.current.identifier}"
                else:
                    url = vc.current.uri
                formatted_queue += f"**{start_index + index + 1} - [{title}]({url}) ({duration}) (Música Atual)**\n"

                title = f"{track.author} - {track.title}"
                duration = Auxiliar.format_time(track.length)
                if track.source == "spotify":
                    url = f"https://open.spotify.com/intl-pt/track/{track.identifier}"
                else:
                    url = track.uri
                formatted_queue += f"**{start_index + index + 2} -** [{title}]({url}) ({duration})"
            else:
                title = f"{track.author} - {track.title}"
                duration = Auxiliar.format_time(track.length)
                if track.source == "spotify":
                    url = f"https://open.spotify.com/intl-pt/track/{track.identifier}"
                else:
                    url = track.uri
                formatted_queue += f"**{start_index + index + 2} -** [{title}]({url}) ({duration})"

            if index < len(queue_list) - 1:
                formatted_queue += "\n"

            if len(formatted_queue) > 4096:
                formatted_queue = formatted_queue[:4093] + "..."
                break

        embed = dc.Embed(title="Músicas na fila", description=formatted_queue, color=000000,
                         timestamp=datetime.datetime.now())
        embed.set_footer(text=f"Página {page_num + 1}/{num_pages}")
        new_queue_message = await ctx.send(embed=embed)

        last_queue_message = new_queue_message

        if num_pages > 1:
            await last_queue_message.add_reaction("⬅️")
            await last_queue_message.add_reaction("➡️")

            def check(reaction_check, user_check):
                return user_check != self.bot.user and str(reaction_check.emoji) in ["⬅️", "➡️"]

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

                    for index, track in enumerate(queue_list[start_index:end_index]):

                        if index == 0 and page_num == 0 and vc.playing:
                            title = f"{vc.current.author} - {vc.current.title}"
                            duration = Auxiliar.format_time(vc.current.length)
                            if vc.current.source == "spotify":
                                url = f"https://open.spotify.com/intl-pt/track/{vc.current.identifier}"
                            else:
                                url = vc.current.uri
                            formatted_queue += f"**{start_index + index + 1} - [{title}]({url}) ({duration}) (Música Atual)**\n"

                            
                            title = f"{track.author} - {track.title}"
                            duration = Auxiliar.format_time(track.length)
                            if track.source == "spotify":
                                url = f"https://open.spotify.com/intl-pt/track/{track.identifier}"
                            else:
                                url = track.uri
                            formatted_queue += f"**{start_index + index + 2} -** [{title}]({url}) ({duration})"
                        else:
                            title = f"{track.author} - {track.title}"
                            duration = Auxiliar.format_time(track.length)
                            if track.source == "spotify":
                                url = f"https://open.spotify.com/intl-pt/track/{track.identifier}"
                            else:
                                url = track.uri
                            formatted_queue += f"**{start_index + index + 2} -** [{title}]({url}) ({duration})"

                        if index < len(queue_list) - 1:
                            formatted_queue += "\n"

                        if len(formatted_queue) > 4096:
                            formatted_queue = formatted_queue[:4093] + "..."
                            break

                    embed.description = formatted_queue
                    embed.set_footer(text=f"Página {page_num + 1}/{num_pages}")
                    await last_queue_message.edit(embed=embed)

                    await reaction.remove(user)
                    page_counts[page_num] += 1

    @commands.command(aliases=['rq'])
    async def removequeue(self, ctx, position: int):

        if ctx.author.voice is None:
            await Auxiliar.send_embed_message(ctx, 'Você não está em um canal de voz!')
            return None

        if ctx.voice_client is None:
            await Auxiliar.send_embed_message(ctx, 'O bot não está em um canal de voz!')
            return None

        elif ctx.voice_client.channel.id != ctx.author.voice.channel.id:
            await Auxiliar.send_embed_message(ctx, 'Você não pode passar o tempo da música com o bot em outro canal '
                                                   'de voz.')

        if position == 1:
            await Auxiliar.send_embed_message(ctx, 'Você não pode remover a música atual. Use `-skip`')
            return

        vc: wl.Player = ctx.voice_client

        if position < 1 or position > len(vc.queue):
            await Auxiliar.send_embed_message(ctx, 'Digite uma posição válida da fila de reprodução')
            return

        deleted = vc.queue[position - 2].title
        await vc.queue.delete(position - 2)

        await Auxiliar.send_embed_message(ctx, f"A música **{deleted}** foi removida da fila de reprodução.")

    @commands.command(aliases=['np'])
    async def nowplaying(self, ctx):

        if ctx.voice_client is None:
            await Auxiliar.send_embed_message(ctx, 'O bot não está em um canal de voz!')
            return None

        vc: wl.Player = ctx.voice_client

        if not vc.playing:
            await Auxiliar.send_embed_message(ctx, "Não tem nada tocando...")
        else:
            np_embed = Auxiliar.create_np_embed(vc.current, vc.queue, vc.current.position)
            await ctx.send(embed=np_embed)

    @commands.command()
    async def shuffle(self, ctx):

        if ctx.author.voice is None:
            await Auxiliar.send_embed_message(ctx, 'Você não está em um canal de voz!')
            return None

        if ctx.voice_client is None:
            await Auxiliar.send_embed_message(ctx, 'O bot não está em um canal de voz!')
            return None

        elif ctx.voice_client.channel.id != ctx.author.voice.channel.id:
            await Auxiliar.send_embed_message(ctx, 'Você não pode passar o tempo da música com o bot em outro canal '
                                                   'de voz.')

        vc: wl.Player = ctx.voice_client

        vc.queue.shuffle()

        await Auxiliar.send_embed_message(ctx, 'A fila de reprodução foi embaralhada.')


async def setup(bot):

    await bot.add_cog(Music(bot))
