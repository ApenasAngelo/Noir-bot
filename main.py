#   discord.py | python-dotenv | youtube_dl | PyNaCl | 
import os
import discord as dc
from discord.ext import commands
from dotenv import load_dotenv
from youtube_dl import YoutubeDL
from discord.utils import get

load_dotenv()
bot = commands.Bot(command_prefix='-', intents = dc.Intents.all())

#COMANDOS DO SISTEMA
@bot.event
async def on_ready():
    print('O bot está ON!'.format(bot))

@bot.command()
async def botoff (ctx):
    if ctx.author.guild_permissions.administrator:
        await ctx.send ('Bot encerrando...')
        await bot.close()
    else:
        ctx.send ('Você não tem permissão para isso!')

#COMANDOS GERAIS
@bot.command()
async def love (ctx):
    await ctx.send ('Eu te amo! <3')


#COMANDOS DE MÚSICA
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
    await ctx.voice_client.disconnect()

@bot.command(aliases = ['p'])
async def play (ctx, url):
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
    voice_channel = get(bot.voice_clients, guild=ctx.guild)
    with YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
        I_URL = info['formats'][0]['url']
        source = await dc.FFmpegOpusAudio.from_probe(I_URL, **FFMPEG_OPTIONS)
        voice_channel.play(source)
        voice_channel.is_playing()
    await ctx.send ('A música começou.')

@bot.command()
async def stop(ctx):
    voice_channel = get(bot.voice_clients, guild=ctx.guild)
    voice_channel.stop()
    await ctx.voice_client.disconnect()
    await ctx.send ('A música parou.')

@bot.command()
async def pause(ctx):
    voice_channel = get(bot.voice_clients, guild=ctx.guild)
    if voice_channel.is_playing():
        voice_channel.pause()
        await ctx.send ('A música foi pausada.')
    else:
        await ctx.send ('Não tem nada tocando...')

@bot.command()
async def resume(ctx):
    voice_channel = get(bot.voice_clients, guild=ctx.guild)
    if voice_channel.is_paused():
        voice_channel.resume()
        await ctx.send ('A música foi resumida.')
    else:
        await ctx.send ('A música não está pausada...')

#TOKEN
bot.run(os.getenv('dc.TOKEN'))