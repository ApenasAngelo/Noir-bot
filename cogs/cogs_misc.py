from discord.ext import commands
from random import randint as rn
import re

from cogs.cogs_auxiliar import Auxiliar


class Misc(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command()
    async def love(self, ctx):

        auxiliar = Auxiliar(self.bot)
        await auxiliar.send_embed_message(ctx, 'Eu te amo! <3')

    @commands.command(aliases=['limpar', 'purge'])
    async def clear(self, ctx, limit: int = 10):

        auxiliar = Auxiliar(self.bot)
        if ctx.author.guild_permissions.administrator:
            if limit < 1:
                await auxiliar.send_embed_message(ctx, 'Digite um valor válido de mensagens para apagar.')
                return

            deleted = await ctx.channel.purge(limit=(limit + 1))
            if limit == 1:
                await auxiliar.send_embed_message(ctx, f"{len(deleted) - 1} mensagem foi deletada.", 3)
            else:
                await auxiliar.send_embed_message(ctx, f"{len(deleted) - 1} mensagens foram deletadas.", 3)

    @commands.command(aliases=['dice', 'dado'])
    async def roll(self, ctx, user_input: str = '1d2'):

        auxiliar = Auxiliar(self.bot)

        match = re.match(r'(?:(\d+)#)?(\d+)d(\d+)([+-]\d+)?', user_input)
        if not match:
            await auxiliar.send_embed_message(ctx, 'Input should be in the format "6#4d6"')
            return

        repeat = int(match.group(1)) if match.group(1) else 1
        dice = int(match.group(2))
        faces = int(match.group(3))
        total_sum = int(match.group(4)) if match.group(4) else 0

        formatted = ""

        if repeat == 1 and dice == 1 and faces == 2 and total_sum == 0:
            rng = rn(1, faces)
            await auxiliar.send_embed_message(ctx, f'{"Cara" if rng == 1 else "Coroa"}')
            return

        for x in range(repeat):
            y = 0
            z = 0
            resultado = 0
            valores = []

            while y < dice:
                rng = rn(1, faces)
                valores.append(rng)
                resultado += rng
                y += 1

            resultado += total_sum

            formatted += f"`[{resultado}]` ⟵ ["

            while z < dice:
                formatted += str(valores[z])
                if z != (dice - 1):
                    formatted += ", "
                z += 1

            if total_sum > 0:
                formatted += f"] {dice}d{faces} + {total_sum}"
            elif total_sum < 0:
                formatted += f"] {dice}d{faces} - {total_sum * (-1)}"
            else:
                formatted += f"] {dice}d{faces}"
            x += 1

            if x != repeat:
                formatted += "\n"

        await auxiliar.send_embed_message(ctx, formatted)


async def setup(bot):

    await bot.add_cog(Misc(bot))
