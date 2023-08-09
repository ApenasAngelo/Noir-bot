import os
import datetime
from dotenv import load_dotenv

import discord as dc
from discord.ext import commands
from discord.utils import get

import wavelink as wl
from wavelink.ext import spotify

import sqlite3

#INICIALIZAÇÃO DO BOT
load_dotenv()
class Bot(commands.Bot):

    def __init__(self) -> None:
        intents = dc.Intents.all()
        intents.message_content = True
        activity = dc.Activity(type=dc.ActivityType.listening, name="vozes...")
        status = dc.Status.do_not_disturb

        super().__init__(intents=intents, command_prefix=os.getenv('prefix'), activity=activity, status=status)

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





#INICIALIZAÇÃO E COMANDOS DA BASE DE DADOS
conn = sqlite3.connect('noir_database.sqlite')
cursor = conn.cursor()

@bot.command()
async def configmusic(ctx, music_channel:dc.TextChannel=None):
    
        if ctx.author.guild_permissions.administrator:

            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='guilds'")
            table_exists = cursor.fetchone() is not None
            
            if not table_exists: 
                initialize_database()

            cursor.execute(f"SELECT guild_id FROM guilds WHERE guild_id = {ctx.guild.id}")
            guild_exists = cursor.fetchone() is not None

            if not guild_exists:
                cursor.execute('INSERT INTO guilds (name, guild_id) VALUES (?, ?)', (ctx.guild.name, ctx.guild.id))
                conn.commit()

            insert_music_channel_id(music_channel)
            await send_embed_message(ctx, f'O canal de música foi definido para {music_channel.mention}.')
    
        else:
            await send_embed_message(ctx, 'Você não tem permissão para isso!')


def initialize_database():

    cursor.execute('''CREATE TABLE guilds
             (name TEXT NOT NULL,
              guild_id INTEGER NOT NULL,
              music_channel_id INTEGER)''')
    conn.commit()
            

def insert_music_channel_id(channel):
    
        cursor.execute('UPDATE guilds SET music_channel_id = ? WHERE guild_id = ?', (channel.id, channel.guild.id))
        conn.commit()


def read_music_channel_id(guild):
    
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='guilds'")
    table_exists = cursor.fetchone() is not None
            
    if not table_exists: 
        initialize_database()

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





#COMANDOS DO SISTEMA
@bot.command()
async def botoff(ctx):

    if str(ctx.author.id) == os.getenv('MyUserID'):
        await send_embed_message(ctx, 'Bot encerrando...')
        conn.close()
        await bot.close()
    else:
        await send_embed_message(ctx, 'Você não tem permissão para isso!')


@bot.event
async def on_guild_join(guild):

    await send_embed_message(guild.system_channel, "Olá, eu sou o Noir! Obrigado por me adicionar ao seu servidor. Digite `-help` para ver meus comandos. Espero que goste de mim! <3")
    await send_embed_message(guild.system_channel, "Digite `-configmusic` para configurar canal aonde são enviadas as músicas tocando.")

    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='guilds'")
    table_exists = cursor.fetchone() is not None
    
    if not table_exists: 
        initialize_database()
    
    cursor.execute('INSERT INTO guilds VALUES (?, ?)', (guild.name, guild.id))
    conn.commit()


@bot.event
async def on_guild_remove(guild):

    cursor.execute('DELETE FROM guilds WHERE guild_id = ?', (guild.id,))
    conn.commit()





#COMANDOS GERAIS
@bot.command()
async def love(ctx):

    await send_embed_message(ctx, 'Eu te amo! <3')


@bot.command()
async def purge(ctx, limit:int=10):

    if ctx.author.guild_permissions.administrator:
        if limit < 1:
            await send_embed_message(ctx, 'Digite um valor válido de mensagens para apagar.')
            return

        deleted = await ctx.channel.purge(limit=limit+1)
        if limit == 1:
            await send_embed_message(ctx, f"{len(deleted)-1} mensagem foi deletada.", 3)
        else:
            await send_embed_message(ctx, f"{len(deleted)-1} mensagens foram deletadas.", 3)





#COMANDOS DE MÚSICA
guild_queue_list = {}


@bot.event
async def on_wavelink_track_end(payload):

    vc: wl.Player = payload.player
    track = payload.track

    if vc.queue.loop:
        return await vc.play(track)
    
    guild_queue_list[f'{vc.guild.id}'].pop(0)

    if len(vc.queue) > 0:
        track = vc.queue.get()
        await vc.play(track)

        if not vc.queue.loop:
            channel_id = read_music_channel_id(vc.guild)
            music_channel = bot.get_channel(channel_id)

            np_embed = create_np_embed(vc.guild)
            await music_channel.send(embed=np_embed)


@bot.command(aliases = ['p'])
async def play(ctx, *, search:str=None):

    if search is None:
        await send_embed_message(ctx, 'Digite o nome de uma música, link do Youtube ou o link do Spotify.')
        return

    channel_id = read_music_channel_id(ctx.guild)
    if channel_id is None:
        await send_embed_message(ctx, 'O canal de música não foi configurado. Digite `-configmusic` para configurar.')
        return

    music_channel = bot.get_channel(channel_id)
    if ctx.author.voice is None:
        await send_embed_message(ctx, 'Você não está em um canal de voz!')
        return

    if ctx.voice_client is None:
        channel = ctx.author.voice.channel
        vc: wl.Player = await channel.connect(cls=wl.Player)

    elif ctx.voice_client.channel.id == ctx.author.voice.channel.id:
        vc: wl.Player = ctx.voice_client

    elif ctx.voice_client.channel.id != ctx.author.voice.channel.id:
        await send_embed_message(ctx, 'O bot já está sendo utilizado em outro canal.')
        return

    track = await process_song_search(ctx, search)
    if not track:
        return

    info = get_music_info(track)

    if f'{ctx.guild.id}' not in guild_queue_list:
        guild_queue_list[f'{ctx.guild.id}'] = []

    guild_queue_list[f'{ctx.guild.id}'].append(info)

    addqueue_embed = create_addqueue_embed(info, ctx.message.author)
    await ctx.send(embed=addqueue_embed)

    vc.queue.put(track)

    if not vc.is_playing():
        await vc.play(vc.queue.get())
        np_embed = create_np_embed(ctx.guild)
        await music_channel.send(embed=np_embed)


@bot.command()
async def join(ctx):

    if ctx.author.voice is None:
        await send_embed_message(ctx, 'Você não está em um canal de voz!')
        return None

    if ctx.voice_client is None:
        channel = ctx.author.voice.channel
        wl.Player = await channel.connect(cls=wl.Player)

    elif ctx.voice_client.channel.id != ctx.author.voice.channel.id:
        await send_embed_message(ctx, 'O bot já está sendo utilizado.')
        return None
    
    else:
        await send_embed_message(ctx, 'O bot já está no seu canal de voz.')


@bot.command()
async def disconnect(ctx):

    if ctx.author.voice is None:
        await send_embed_message(ctx, 'Você não está em um canal de voz!')
        return None
    
    if ctx.voice_client is None:
        await send_embed_message(ctx, 'O bot não está em um canal de voz!')
        return None
    
    elif ctx.voice_client.channel.id != ctx.author.voice.channel.id:
        await send_embed_message(ctx, 'Você não pode desconectar o bot em outro canal de voz.')
        return None
    
    vc: wl.Player = ctx.voice_client
    await vc.disconnect()


@bot.command()
async def stop(ctx):

    if ctx.author.voice is None:
        await send_embed_message(ctx, 'Você não está em um canal de voz!')
        return None
    
    if ctx.voice_client is None:
        await send_embed_message(ctx, 'O bot não está em um canal de voz!')
        return None
    
    elif ctx.voice_client.channel.id != ctx.author.voice.channel.id:
        await send_embed_message(ctx, 'Você não pode parar a música com o bot em outro canal de voz.')
        return None
    
    vc: wl.Player = ctx.voice_client

    await vc.stop()
    await vc.disconnect()
    await send_embed_message(ctx, 'A música parou.')
    guild_queue_list[f'{ctx.guild.id}'].clear()


@bot.command()
async def pause(ctx):

    if ctx.author.voice is None:
        await send_embed_message(ctx, 'Você não está em um canal de voz!')
        return None
    
    if ctx.voice_client is None:
        await send_embed_message(ctx, 'O bot não está em um canal de voz!')
        return None
    
    elif ctx.voice_client.channel.id != ctx.author.voice.channel.id:
        await send_embed_message(ctx, 'Você não pode pausar a música com o bot em outro canal de voz.')
        return None
    
    vc: wl.Player = ctx.voice_client

    if vc.is_playing():
        await vc.pause()
        await send_embed_message(ctx, 'A música foi pausada.')

    else:
        await send_embed_message(ctx, 'Não tem nada tocando...')


@bot.command()
async def resume(ctx):

    if ctx.author.voice is None:
        await send_embed_message(ctx, 'Você não está em um canal de voz!')
        return None
    
    if ctx.voice_client is None:
        await send_embed_message(ctx, 'O bot não está em um canal de voz!')
        return None
    
    elif ctx.voice_client.channel.id != ctx.author.voice.channel.id:
        await send_embed_message(ctx, 'Você não pode resumir a música com o bot em outro canal de voz.')
        return None
    
    vc: wl.Player = ctx.voice_client

    if vc.is_paused():
        await vc.resume()
        await send_embed_message(ctx, 'A música foi resumida.')

    else:
        await send_embed_message(ctx, 'A música não está pausada...')


@bot.command()
async def skip(ctx):

    if ctx.author.voice is None:
        await send_embed_message(ctx, 'Você não está em um canal de voz!')
        return None
    
    if ctx.voice_client is None:
        await send_embed_message(ctx, 'O bot não está em um canal de voz!')
        return None
    
    elif ctx.voice_client.channel.id != ctx.author.voice.channel.id:
        await send_embed_message(ctx, 'Você não pode pular a música com o bot em outro canal de voz.')
    
    vc: wl.Player = ctx.voice_client

    if vc.is_playing():
        await vc.stop()
    else:
        await send_embed_message(ctx, 'Não tem nada tocando...')


@bot.command()
async def seek(ctx, time:int):

    if ctx.author.voice is None:
        await send_embed_message(ctx, 'Você não está em um canal de voz!')
        return None
    
    if ctx.voice_client is None:
        await send_embed_message(ctx, 'O bot não está em um canal de voz!')
        return None
    
    elif ctx.voice_client.channel.id != ctx.author.voice.channel.id:
        await send_embed_message(ctx, 'Você não pode passar o tempo da música com o bot em outro canal de voz.')

    vc: wl.Player = ctx.voice_client
    await vc.seek(time*1000)


@bot.command(aliases = ['q'])
async def queue(ctx):

    if ctx.voice_client is None:
        await send_embed_message(ctx, 'O bot não está em um canal de voz!')
        return None
    
    if ctx.voice_client is None:
        await send_embed_message(ctx, 'O bot não está em um canal de voz!')
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


@bot.command(aliases = ['rq'])
async def removequeue(ctx, position:int):

    if ctx.author.voice is None:
        await send_embed_message(ctx, 'Você não está em um canal de voz!')
        return None
    
    if ctx.voice_client is None:
        await send_embed_message(ctx, 'O bot não está em um canal de voz!')
        return None
    
    elif ctx.voice_client.channel.id != ctx.author.voice.channel.id:
        await send_embed_message(ctx, 'Você não pode passar o tempo da música com o bot em outro canal de voz.')

    if position == 1:
        await send_embed_message(ctx, 'Você não pode remover a música atual. Use `-skip`')
        return
    
    if position < 1 or position > len(guild_queue_list[f'{ctx.guild.id}']):
        await send_embed_message(ctx, 'Digite uma posição válida da fila de reprodução')
        return
    
    vc: wl.Player = ctx.voice_client
    deleted = guild_queue_list[f'{ctx.guild.id}'][position-1]['title']
    guild_queue_list[f'{ctx.guild.id}'].pop(position-1)
    del vc.queue[position-2]

    await send_embed_message(ctx, f"A música **{deleted}** foi removida da fila de reprodução.")


@bot.command(aliases = ['np'])
async def nowplaying(ctx):

    if ctx.voice_client is None:
        await send_embed_message(ctx, 'O bot não está em um canal de voz!')
        return None
    
    vc: wl.Player = ctx.voice_client

    if not vc.is_playing():
        await send_embed_message(ctx, "Não tem nada tocando...")
    else:
        np_embed = create_np_embed(ctx.guild)
        await ctx.send(embed=np_embed)
    





#FUNÇÕES AUXILIARES
async def process_song_search(ctx, search:str):

    if "open.spotify.com" in search:
        decoded = spotify.decode_url(search)
        if not decoded or decoded['type'] is not spotify.SpotifySearchType.track:
            await send_embed_message(ctx, 'Só links de músicas do Spotify são válidos.')
            return
    
        tracks: list[spotify.SpotifyTrack] = await spotify.SpotifyTrack.search(search)
        if tracks is None:
            await send_embed_message(ctx, 'Esse link do Spotify não é válido.')
            return

        track: spotify.SpotifyTrack = tracks[0]
        return track
    else:
        tracks = await wl.YouTubeTrack.search(search)
        if not tracks:
            await send_embed_message(ctx, f'Nenhum resultado encontrado com: `{search}`')
            return

        track = tracks[0]
        return track


async def send_embed_message(ctx, message:str = None, deletetime:float = None):

        msg_embed = dc.Embed(description=message, color=000000)
        await ctx.send(embed=msg_embed, delete_after=deletetime)


def create_np_embed(guild):

    title = guild_queue_list[f'{guild.id}'][0]['title']
    thumbnail = guild_queue_list[f'{guild.id}'][0]['thumbnail']
    duration = guild_queue_list[f'{guild.id}'][0]['duration']
    url = guild_queue_list[f'{guild.id}'][0]['url']
    
    embed = dc.Embed(title=":musical_note: • Reproduzindo:", description=f"[{title}]({url})", color=0x5aacea, timestamp=datetime.datetime.now())
    embed.set_thumbnail(url=thumbnail)
    embed.add_field(name="Duração:", value=duration, inline=False)

    if len(guild_queue_list[f'{guild.id}']) > 1:
        embed.set_footer(text=f"Próxima: {guild_queue_list[f'{guild.id}'][1]['title']}")
    else:
        embed.set_footer(text=f"Próxima: Nenhuma...")

    return embed


def create_addqueue_embed(info, author):

    title = info['title']
    duration = info['duration']
    url = info['url']
    
    embed = dc.Embed(description=f":white_check_mark: **• Adicionado a fila >** [{title}]({url}) | ({duration})", color=0x6fa64f, timestamp=datetime.datetime.now())
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





#COMANDOS DE DEBUG
@bot.command()
async def teste(ctx):

    channel_id = read_music_channel_id(ctx.guild)
    if id is None:
        await ctx.send('Não há canal de música definido para esse servidor.')
    else:
        await ctx.send(channel_id)

    music_channel = bot.get_channel(channel_id)
    await music_channel.send('Teste')


@bot.command()
async def tq(ctx):
    vc: wl.Player = ctx.voice_client
    await ctx.send(str(vc.queue))
    await ctx.send(len(vc.queue))





#TOKEN
bot.run(os.getenv('dc.TOKEN'))