#   discord.py | python-dotenv | yt_dlp | PyNaCl | asyncio | Wavelink | 
import os
from dotenv import load_dotenv

import discord as dc
from discord.ext import commands
from discord.utils import get

import urllib.parse, urllib.request, re
import yt_dlp
import asyncio
import wavelink as wl
from wavelink.ext import spotify
import datetime

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
        await wl.NodePool.connect(client=self, nodes=[node])

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
ytdl_options = {
    'skip_download': True,
    'extract_flat': True,
    'youtube_include_dash_manifest': False,
    'youtube_skip_dash_manifest': True,
    'force_generic_extractor': True,
    }

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


    tracks = await wl.YouTubeTrack.search(search)
    if not tracks:
        await ctx.send(f'Nenhum resultado encontrado com: `{search}`')
        return

    track = tracks[0]

    if not vc.is_playing():
        await vc.play(track)
    else:
        await vc.queue.put_wait(track)

    info = get_music_info(search)
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
async def seek(ctx, time: int):
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
    await ctx.send (song_list)

@bot.command()
async def teste(ctx):
    await ctx.send (ctx.voice_client.channel.id)
    await ctx.send (ctx.author.voice.channel.id)

#FUNÇÕES AUXILIARES
async def process_song_search(ctx, search):
    tracks = await wl.YouTubeTrack.search(search)
    if not tracks:
        await ctx.send(f'Nenhum resultado encontrado com: `{search}`')
        return

    track = tracks[0]
    return track

def create_music_embed(info, author):
    title = info.get('title', None)
    thumbnail = info.get('thumbnail', None)
    duration = info.get('duration', None)

    duration_minutes = int(duration / 60)
    duration_seconds = int(duration % 60)
    duration_formatted = "{:d}:{:02d}".format(duration_minutes, duration_seconds)

    url = info['webpage_url']
    
    embed = dc.Embed(description="", color=000000, timestamp=datetime.datetime.now())
    embed.set_thumbnail(url=thumbnail)
    embed.add_field(name="Adicionado a fila de reprodução:", value=f"[{title}]({url})", inline=False)
    embed.add_field(name="Duração:", value=duration_formatted, inline=False)
    embed.set_footer(text="Adicionado por "+format(author.display_name), icon_url=author.avatar)

    return embed

def get_music_info(search):
    with yt_dlp.YoutubeDL(ytdl_options) as ydl:
        if "http" in search:
            url = search
            info = ydl.extract_info(url, download=False)
        else:
            query_string = urllib.parse.urlencode({'search_query': search})
            htm_content = urllib.request.urlopen('http://www.youtube.com/results?' + query_string)
            search_results = re.findall(r'/watch\?v=(.{11})', htm_content.read().decode())
            url = ('http://www.youtube.com/watch?v=' + search_results[0])
            info = ydl.extract_info(url, download=False)

    return info

#TOKEN
bot.run(os.getenv('dc.TOKEN'))