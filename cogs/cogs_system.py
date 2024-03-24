import os

from discord.ext import commands

from globals import conn, cursor
from cogs.cogs_database import Database
from cogs.cogs_auxiliar import Auxiliar


class System(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):

        auxiliar = Auxiliar(self.bot)
        await auxiliar.send_embed_message(
            guild.system_channel,
            "Olá, eu sou o Noir! Obrigado por me adicionar ao seu servidor. Digite `-help` para ver meus comandos. Espero que goste de mim! <3",
        )
        await auxiliar.send_embed_message(
            guild.system_channel,
            "Digite `-configmusic` para configurar o canal aonde são enviadas as músicas tocando.",
        )
        await auxiliar.send_embed_message(
            guild.system_channel,
            "Digite `-configgreetings` para configurar o canal aonde são enviadas as boas vindas.",
        )
        await auxiliar.send_embed_message(
            guild.system_channel,
            "Digite `-configrole` para configurar o cargo que é dado a todas as pessoas quando entram.",
        )

        cursor.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='guilds'"
        )
        table_exists = cursor.fetchone() is not None

        if not table_exists:
            database = Database(self.bot)
            database.initialize_database()

        cursor.execute("INSERT INTO guilds VALUES (?, ?)", (guild.name, guild.id))
        conn.commit()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):

        cursor.execute("DELETE FROM guilds WHERE guild_id = ?", (guild.id,))
        conn.commit()

    @commands.Cog.listener()
    async def on_member_join(self, member):

        auxiliar = Auxiliar(self.bot)
        database = Database(self.bot)

        greetings_channel_id = database.read_greetings_channel_id(member.guild)
        if greetings_channel_id is not None:
            await auxiliar.send_embed_message(
                self.bot.get_channel(greetings_channel_id),
                f"Olá {member.mention}, seja bem vindo(a) ao servidor {member.guild.name}",
            )

        member_role_id = database.read_member_role_id(member.guild)
        if member_role_id is not None:
            await member.add_roles(member.guild.get_role(member_role_id))

        return

    @commands.command()
    async def botoff(self, ctx):

        auxiliar = Auxiliar(self.bot)
        if str(ctx.author.id) == os.getenv("MyUserID"):
            await auxiliar.send_embed_message(ctx, "Bot encerrando...")
            conn.close()
            await self.bot.close()
        else:
            await auxiliar.send_embed_message(ctx, "Você não tem permissão para isso!")

    @commands.command()
    async def reloadcogs(self, ctx):

        auxiliar = Auxiliar(self.bot)
        for cog in self.bot.cogs:
            self.bot.reload_extension(f"cogs.cogs_{cog.lower()}")
            print(f"Reloaded Cog: {cog}")
        await auxiliar.send_embed_message(ctx, "Cogs recarregadas.")


async def setup(bot):

    await bot.add_cog(System(bot))
