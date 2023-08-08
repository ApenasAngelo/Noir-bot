#   discord.py | python-dotenv | youtube_dl | PyNaCl | asyncio | 
import os
import discord as dc
import urllib.parse, urllib.request, re
from discord.ext import commands
from dotenv import load_dotenv
from yt_dlp import YoutubeDL
from discord.utils import get
from asyncio import coroutines,run

load_dotenv()
bot = commands.Bot(command_prefix='-', intents = dc.Intents.all())

#COMANDOS DO SISTEMA
@bot.event
async def on_ready():
    print('O bot está ON!'.format(bot))

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

async def play_next(ctx) -> coroutines:
    if len(song_list) >= 1:
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        del song_list[0]
        source = await dc.FFmpegOpusAudio.from_probe(song_list[0], **FFMPEG_OPTIONS, method = 'native')
        voice_channel = get(bot.voice_clients, guild = ctx.guild)
        voice_channel.play(source, after = lambda x: play_next(ctx))

@bot.command()
async def join (ctx):
    if ctx.author.voice is None:
        await ctx.send ('Você não está em um canal de voz!')
        return None
    voice_channel = bot.get_channel(ctx.author.voice.channel.id)
    if ctx.voice_client is None:
        await voice_channel.connect()
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
    await ctx.voice_client.disconnect()

@bot.command(aliases = ['p'])
async def play (ctx, *, search):
    YDL_OPTIONS = {'format': 'bestaudio/best', 'noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    if ctx.author.voice is None:
        await ctx.send ('Você não está em um canal de voz!')
        return None
    voice_channel = bot.get_channel(ctx.author.voice.channel.id)
    if ctx.voice_client is None:
        await voice_channel.connect()
    elif ctx.voice_client.channel.id != ctx.author.voice.channel.id:
        await ctx.send ('O bot já está sendo utilizado.')
        return None
    else:
        print ('O bot já está nesse canal. Proseguindo...')
    voice_channel = get(bot.voice_clients, guild = ctx.guild)
    with YoutubeDL(YDL_OPTIONS) as ydl:
        query_string = urllib.parse.urlencode({'search_query': search})
        htm_content = urllib.request.urlopen('http://www.youtube.com/results?' + query_string)
        search_results = re.findall(r'/watch\?v=(.{11})', htm_content.read().decode())
        url = ('http://www.youtube.com/watch?v=' + search_results[0])
        info = ydl.extract_info(url, download=False)
        I_URL = info['webpage_url']
        song_list.append(I_URL)
        if not voice_channel.is_playing():
            if len(song_list) > 1:
                del song_list[0]
            source = await dc.FFmpegOpusAudio.from_probe(song_list[0], **FFMPEG_OPTIONS, method = 'native')
            voice_channel.play(source, after = lambda x: run (play_next(ctx)))
            voice_channel.is_playing()
            await ctx.send ('A música começou.')
        else:
            await ctx.send ('Música adicionada a fila de reprodução.')

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
    voice_channel = get(bot.voice_clients, guild=ctx.guild)
    voice_channel.stop()
    await ctx.voice_client.disconnect()
    del song_list[:]
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
    voice_channel = get(bot.voice_clients, guild=ctx.guild)
    if voice_channel.is_playing():
        voice_channel.pause()
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
    voice_channel = get(bot.voice_clients, guild=ctx.guild)
    if voice_channel.is_paused():
        voice_channel.resume()
        await ctx.send ('A música foi resumida.')
    else:
        await ctx.send ('A música não está pausada...')

@bot.command()
async def skip(ctx):
    if ctx.author.voice is None:
        await ctx.send ('Você não está em um canal de voz!')
        return None
    voice_channel = bot.get_channel(ctx.author.voice.channel.id)
    if ctx.voice_client is None:
        await voice_channel.connect()
    elif ctx.voice_client.channel.id != ctx.author.voice.channel.id:
        await ctx.send ('Você não pode pular a música em outro canal de voz.')
        return None
    else:
        print ('O bot já está nesse canal. Proseguindo...')
    voice_channel = get(bot.voice_clients, guild = ctx.guild)
    voice_channel.stop()
    await play_next(ctx)
    
    

@bot.command()
async def search(ctx, *, search):
    query_string = urllib.parse.urlencode({'search_query': search})
    htm_content = urllib.request.urlopen('http://www.youtube.com/results?' + query_string)
    search_results = re.findall(r'/watch\?v=(.{11})', htm_content.read().decode())
    url = ('http://www.youtube.com/watch?v=' + search_results[0])
    await ctx.send (url)

@bot.command()                       
async def addqueue(ctx, *, search):
    YDL_OPTIONS = {'format': 'bestaudio/best', 'noplaylist': 'True'}
    query_string = urllib.parse.urlencode({'search_query': search})
    htm_content = urllib.request.urlopen('http://www.youtube.com/results?' + query_string)
    search_results = re.findall(r'/watch\?v=(.{11})', htm_content.read().decode())
    url = ('http://www.youtube.com/watch?v=' + search_results[0])
    with YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
        I_URL = info['formats'][0]['url']
        song_list.insert(len(song_list), I_URL)
        await ctx.send (len(song_list))

@bot.command(aliases = ['q'])
async def queue(ctx):
    await ctx.send (song_list)

@bot.command()
async def teste(ctx):
    await ctx.send (ctx.author.id)
    await ctx.send (os.getenv('MyUserID'))

#TOKEN
bot.run(os.getenv('dc.TOKEN'))