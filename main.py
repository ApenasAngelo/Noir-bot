import os
from dotenv import load_dotenv

import discord as dc
from discord.ext import commands
from discord.utils import get

import wavelink as wl
from wavelink.ext import spotify
import datetime
import asyncio

load_dotenv()
class Bot(commands.Bot):

    def __init__(self) -> None:
        intents = dc.Intents.all()
        intents.message_content = True

        super().__init__(intents=intents, command_prefix=os.getenv('prefix'))

    async def on_ready(self) -> None:
        print('O bot está ON!'.format(bot))

    async def setup_hook(self) -> None:
        sc = spotify.SpotifyClient(
            client_id=os.getenv('spotify.ClientID'),
            client_secret=os.getenv('spotify.ClientSecret')
        )

        node: wl.Node = wl.Node(uri=os.getenv('wl.URI'), password=os.getenv('wl.PASSWORD'))
        await wl.NodePool.connect(client=self, nodes=[node], spotify=sc)

bot = Bot()





#COMANDOS DO SISTEMA
@bot.command()
async def botoff (ctx):
    if str(ctx.author.id) == os.getenv('MyUserID'):
        await ctx.send ('Bot encerrando...')
        await bot.close()
    else:
        await ctx.send ('Você não tem permissão para isso!')





#COMANDOS GERAIS
@bot.command()
async def love (ctx):
    await ctx.send ('Eu te amo! <3')





#COMANDOS DE MÚSICA
song_list = []

@bot.command(aliases = ['p'])
async def play (ctx, *, search):
    if ctx.author.voice is None:
        await ctx.send('Você não está em um canal de voz!')
        return

    if ctx.voice_client is None:
        channel = ctx.author.voice.channel
        vc: wl.Player = await channel.connect(cls=wl.Player)

    elif ctx.voice_client.channel.id == ctx.author.voice.channel.id:
        vc: wl.Player = ctx.voice_client

    elif ctx.voice_client.channel.id != ctx.author.voice.channel.id:
        await ctx.send('O bot já está sendo utilizado em outro canal.')
        return

    track = await process_song_search(ctx, search)
    if not track:
        return

    await vc.queue.put_wait(track)

    if not vc.is_playing():
        await vc.play(vc.queue.get())

    info = get_music_info(track)
    song_list.append(info)
    song_embed = create_music_embed(info, ctx.message.author)
    await ctx.send(embed=song_embed)

@bot.command()
async def join (ctx):
    if ctx.author.voice is None:
        await ctx.send ('Você não está em um canal de voz!')
        return None

    if ctx.voice_client is None:
        channel = ctx.author.voice.channel
        wl.Player = await channel.connect(cls=wl.Player)

    elif ctx.voice_client.channel.id != ctx.author.voice.channel.id:
        await ctx.send ('O bot já está sendo utilizado.')
        return None
    
    else:
        await ctx.send ('O bot já está no seu canal de voz.')

@bot.command()
async def disconnect (ctx):

    if ctx.author.voice is None:
        await ctx.send ('Você não está em um canal de voz!')
        return None
    
    if ctx.voice_client is None:
        await ctx.send ('O bot não está em um canal de voz!')
        return None
    
    elif ctx.voice_client.channel.id != ctx.author.voice.channel.id:
        await ctx.send ('Você não pode desconectar o bot em outro canal de voz.')
        return None
    
    vc: wl.Player = ctx.voice_client
    await vc.disconnect()

@bot.command()
async def stop(ctx):

    if ctx.author.voice is None:
        await ctx.send ('Você não está em um canal de voz!')
        return None
    
    if ctx.voice_client is None:
        await ctx.send ('O bot não está em um canal de voz!')
        return None
    
    elif ctx.voice_client.channel.id != ctx.author.voice.channel.id:
        await ctx.send ('Você não pode parar a música com o bot em outro canal de voz.')
        return None
    
    vc: wl.Player = ctx.voice_client

    await vc.stop()
    await vc.disconnect()
    await ctx.send ('A música parou.')

@bot.command()
async def pause(ctx):

    if ctx.author.voice is None:
        await ctx.send ('Você não está em um canal de voz!')
        return None
    
    if ctx.voice_client is None:
        await ctx.send ('O bot não está em um canal de voz!')
        return None
    
    elif ctx.voice_client.channel.id != ctx.author.voice.channel.id:
        await ctx.send ('Você não pode pausar a música com o bot em outro canal de voz.')
        return None
    
    vc: wl.Player = ctx.voice_client

    if vc.is_playing():
        await vc.pause()
        await ctx.send ('A música foi pausada.')

    else:
        await ctx.send ('Não tem nada tocando...')

@bot.command()
async def resume(ctx):

    if ctx.author.voice is None:
        await ctx.send ('Você não está em um canal de voz!')
        return None
    
    if ctx.voice_client is None:
        await ctx.send ('O bot não está em um canal de voz!')
        return None
    
    elif ctx.voice_client.channel.id != ctx.author.voice.channel.id:
        await ctx.send ('Você não pode resumir a música com o bot em outro canal de voz.')
        return None
    
    vc: wl.Player = ctx.voice_client

    if vc.is_paused():
        await vc.resume()
        await ctx.send ('A música foi resumida.')

    else:
        await ctx.send ('A música não está pausada...')

@bot.command()
async def skip(ctx):
    if ctx.author.voice is None:
        await ctx.send ('Você não está em um canal de voz!')
        return None
    
    if ctx.voice_client is None:
        await ctx.send ('O bot não está em um canal de voz!')
        return None
    
    elif ctx.voice_client.channel.id != ctx.author.voice.channel.id:
        await ctx.send ('Você não pode pular a música com o bot em outro canal de voz.')
    
    vc: wl.Player = ctx.voice_client

    if vc.is_playing():
        await vc.stop(force=True)
    else:
        await ctx.send('Não tem nada tocando...')
    
@bot.command()
async def seek(ctx, time:int):
    if ctx.author.voice is None:
        await ctx.send ('Você não está em um canal de voz!')
        return None
    
    if ctx.voice_client is None:
        await ctx.send ('O bot não está em um canal de voz!')
        return None
    
    elif ctx.voice_client.channel.id != ctx.author.voice.channel.id:
        await ctx.send ('Você não pode passar o tempo da música com o bot em outro canal de voz.')

    vc: wl.Player = ctx.voice_client
    await vc.seek(time*1000)


@bot.command(aliases = ['q'])
async def queue(ctx):
    vc: wl.Player = ctx.voice_client
    
    formatted_queue = ""

    for index, song in enumerate(song_list):
        if index == 0 and vc.is_playing():
            formatted_queue += f"**{index+1} - [{song['title']}]({song['url']}) ({song['duration']}) (Música Atual)**"
        else:
            formatted_queue += f"**{index+1} -** [{song['title']}]({song['url']}) ({song['duration']})"

        if index < len(song_list) - 1:
            formatted_queue += "\n"
        
    embed = dc.Embed(title="Músicas na fila", description=formatted_queue, color=000000, timestamp=datetime.datetime.now())
    await ctx.send(embed=embed)

@bot.command(aliases = ['np'])
async def nowplaying (ctx):
    vc: wl.Player = ctx.voice_client

    if not vc.is_playing():
        await ctx.send("Não tem nada tocando...")
    else:
        await ctx.send(vc.current())
    





#FUNÇÕES AUXILIARES
async def process_song_search(ctx, search:str):
    if "open.spotify.com" in search:
        decoded = spotify.decode_url(search)
        if not decoded or decoded['type'] is not spotify.SpotifySearchType.track:
            await ctx.send('Só links de músicas do Spotify são válidos.')
            return
    
        tracks: list[spotify.SpotifyTrack] = await spotify.SpotifyTrack.search(search)
        if tracks is None:
            await ctx.send('Esse link do Spotify não é válido.')
            return

        track: spotify.SpotifyTrack = tracks[0]
        return track
    else:
        tracks = await wl.YouTubeTrack.search(search)
        if not tracks:
            await ctx.send(f'Nenhum resultado encontrado com: `{search}`')
            return

        track = tracks[0]
        return track

def create_music_embed(info, author):
    title = info['title']
    thumbnail = info['thumbnail']
    duration = info['duration']
    url = info['url']
    
    embed = dc.Embed(title="Adicionado a fila de reprodução:", description=f"[{title}]({url})", color=000000, timestamp=datetime.datetime.now())
    embed.set_thumbnail(url=thumbnail)
    embed.add_field(name="Duração:", value=duration, inline=False)
    embed.set_footer(text="Adicionado por "+format(author.display_name), icon_url=author.avatar)

    return embed

def get_music_info(track):
    total_seconds = track.length / 1000  # Convert milliseconds to seconds

    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)

    if hours > 0:
        duration_formatted = "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)
    else:
        duration_formatted = "{:02d}:{:02d}".format(minutes, seconds)

    if isinstance(track, spotify.SpotifyTrack):
        info = {
            'track': track,
            'title': f"{track.artists[0]} - {track.name}",
            'thumbnail': track.images[0],
            'duration': duration_formatted,
            'url':  f"https://open.spotify.com/intl-pt/track/{track.id}"
        }
    else:
        info = {
            'track': track,
            'title': track.title,
            'thumbnail': track.thumbnail,
            'duration': duration_formatted,
            'url': track.uri
        }

    return info

#TOKEN
bot.run(os.getenv('dc.TOKEN'))