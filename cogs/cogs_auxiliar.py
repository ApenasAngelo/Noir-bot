import datetime

import discord as dc
from discord.ext import commands

import wavelink as wl
from wavelink.ext import spotify
import spotipy

from globals import guild_queue_list, spotipy


class Auxiliar(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot


    async def process_song_search(self, ctx, search:str):

        if "open.spotify.com" in search:
            decoded: spotify.SpotifyDecodePayload = spotify.decode_url(search)

            if decoded is not None and decoded.type is not spotify.SpotifySearchType.unusable:

                if decoded.type is spotify.SpotifySearchType.album:
                    album: list[spotify.SpotifyTrack] = await spotify.SpotifyTrack.search(search)
                    if album is None:
                        await self.send_embed_message(ctx, 'Esse álbum do Spotify não é válido.')
                        return

                    return 'album', album


                elif decoded.type is spotify.SpotifySearchType.playlist:
                    playlist: list[spotify.SpotifyTrack] = await spotify.SpotifyTrack.search(search)
                    if playlist is None:
                        await self.send_embed_message(ctx, 'Essa playlist do Spotify não é válida.')
                        return
                    
                    playlist_id = search[search.find("/playlist/") + len("/playlist/"):][:22]
                    playlist_details = spotipy.playlist(playlist_id)

                    return 'playlist', playlist_details['name'], playlist


                if decoded.type is spotify.SpotifySearchType.track:
                    songs: list[spotify.SpotifyTrack] = await spotify.SpotifyTrack.search(search)
                    if songs is None:
                        await self.send_embed_message(ctx, 'Esse link do Spotify não é válido.')
                        return

                    return songs[0]


            else:
                await self.send_embed_message(ctx, 'Este link do Spotify é inválido.')
                return
        
        elif "youtube.com" in search or "youtu.be" in search:
            if "?list=" in search or "&list=" in search:
                tracks = await wl.YouTubePlaylist.convert(ctx, search)
                if not tracks:
                    await self.send_embed_message(ctx, f'Nenhum resultado encontrado com: `{search}`')
                    return
                
                return tracks

            elif "youtu.be" in search:
                    song_ID = search[-11:]
                    tracks = await wl.YouTubeTrack.search(f'https://www.youtube.com/watch?v={song_ID}')
                    if not tracks:
                        await self.send_embed_message(ctx, f'Nenhum resultado encontrado com: `{search}`')
                        return

                    return tracks[0]
        
        else:
            tracks = await wl.YouTubeTrack.search(search)
            if not tracks:
                await self.send_embed_message(ctx, f'Nenhum resultado encontrado com: `{search}`')
                return
            
            return tracks[0]


    async def send_embed_message(self, ctx, message:str = None, deletetime:float = None):

        msg_embed = dc.Embed(description=message, color=000000)
        await ctx.send(embed=msg_embed, delete_after=deletetime)


    def create_np_embed(self, guild, position:int = None):

        title = guild_queue_list[f'{guild.id}'][0]['title']
        thumbnail = guild_queue_list[f'{guild.id}'][0]['thumbnail']
        duration = guild_queue_list[f'{guild.id}'][0]['duration']
        url = guild_queue_list[f'{guild.id}'][0]['url']

        embed = dc.Embed(title=":musical_note: • Reproduzindo:", description=f"[{title}]({url})", color=0x5aacea, timestamp=datetime.datetime.now())
        embed.set_thumbnail(url=thumbnail)

        if position:
            total_seconds = position / 1000

            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            seconds = int(total_seconds % 60)

            if hours > 0:
                current_time = "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)
            else:
                current_time = "{:02d}:{:02d}".format(minutes, seconds)

            embed.add_field(name="Duração:", value=f'{current_time} - {duration}', inline=False)
        else:
            embed.add_field(name="Duração:", value=f'{duration}', inline=False)

        if len(guild_queue_list[f'{guild.id}']) > 1:
            embed.set_footer(text=f"Próxima: {guild_queue_list[f'{guild.id}'][1]['title']}")
        else:
            embed.set_footer(text=f"Próxima: Nenhuma...")

        return embed


    def create_addqueue_embed(self, info, author):

        title = info['title']
        duration = info['duration']
        url = info['url']
        
        embed = dc.Embed(description=f":white_check_mark: **• Adicionado a fila >** [{title}]({url}) | ({duration})", color=0x6fa64f, timestamp=datetime.datetime.now())
        embed.set_footer(text="Adicionado por "+format(author.display_name), icon_url=author.avatar)

        return embed


    def create_addqueue_pl_embed(self, title, length, author):

        embed = dc.Embed(description=f":white_check_mark: **• Adicionado a fila >** Playlist **{title}** com **{length}** músicas", color=0x6fa64f, timestamp=datetime.datetime.now())
        embed.set_footer(text="Adicionado por "+format(author.display_name), icon_url=author.avatar)

        return embed


    def create_addqueue_spotify_album_embed(self, title, length, author):

        embed = dc.Embed(description=f":white_check_mark: **• Adicionado a fila >** Álbum **{title}** com **{length}** músicas", color=0x6fa64f, timestamp=datetime.datetime.now())
        embed.set_footer(text="Adicionado por "+format(author.display_name), icon_url=author.avatar)

        return embed


    def create_addqueue_spotify_pl_embed(self, title, length, author):

        embed = dc.Embed(description=f":white_check_mark: **• Adicionado a fila >** Playlist **{title}** com **{length}** músicas", color=0x6fa64f, timestamp=datetime.datetime.now())
        embed.set_footer(text="Adicionado por "+format(author.display_name), icon_url=author.avatar)

        return embed


    def get_music_info(self, track):

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
                'title': f"{track.artists[0]} - {track.title}",
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


async def setup(bot):
    await bot.add_cog(Auxiliar(bot))