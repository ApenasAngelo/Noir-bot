import datetime
import re

import discord as dc
from discord.ext import commands

import wavelink as wl


class Auxiliar(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot


    @staticmethod
    async def send_embed_message(ctx, message: str = None, deletetime: float = None) -> None:

        msg_embed = dc.Embed(description=message, color=000000)
        await ctx.send(embed=msg_embed, delete_after=deletetime)

    @staticmethod
    def create_np_embed(track: wl.Playable, queue: wl.Queue, position: int = None) -> dc.Embed:

        title = f"{track.author} - {track.title}"
        thumbnail = track.artwork
        duration = Auxiliar.format_time(track.length)
        if track.source == "spotify":
            url = f"https://open.spotify.com/intl-pt/track/{track.identifier}"
        else:
            url = track.uri

        embed = dc.Embed(title=":musical_note: • Reproduzindo:", description=f"[{title}]({url})", color=0x5aacea,
                         timestamp=datetime.datetime.now())
        embed.set_thumbnail(url=thumbnail)

        if position:
            embed.add_field(name="Duração:", value=f'{Auxiliar.format_time(position)} / {duration}', inline=False)
        else:
            embed.add_field(name="Duração:", value=f'{duration}', inline=False)

        if len(queue) >= 1:
            embed.set_footer(text=f"Próxima: {queue[0].author} - {queue[0].title}")
        else:
            embed.set_footer(text=f"Próxima: Nenhuma...")

        return embed

    @staticmethod
    def create_addqueue_embed(track: wl.Playable, author) -> dc.Embed:

        title = f"{track.author} - {track.title}"
        duration = Auxiliar.format_time(track.length)
        if track.source == "spotify":
            url = f"https://open.spotify.com/intl-pt/track/{track.identifier}"
        else:
            url = track.uri

        embed = dc.Embed(description=f":white_check_mark: **• Adicionado a fila >** [{title}]({url}) | ({duration})",
                         color=0x6fa64f, timestamp=datetime.datetime.now())
        embed.set_footer(text="Adicionado por " + format(author.display_name), icon_url=author.avatar)

        return embed

    @staticmethod
    def create_addqueue_pl_embed(pl: wl.Playlist, author) -> dc.Embed:

        embed = dc.Embed(
            description=f":white_check_mark: **• Adicionado a fila >** Playlist **{pl.name}** com **{len(pl.tracks)}** músicas",
            color=0x6fa64f, timestamp=datetime.datetime.now())
        embed.set_footer(text="Adicionado por " + format(author.display_name), icon_url=author.avatar)

        return embed

    @staticmethod
    def format_time(length: int) -> str:

        total_seconds = length / 1000  # Convert milliseconds to seconds

        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)

        if hours > 0:
            duration_formatted = "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)
        else:
            duration_formatted = "{:02d}:{:02d}".format(minutes, seconds)

        return duration_formatted

async def setup(bot):

    await bot.add_cog(Auxiliar(bot))
