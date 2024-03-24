import discord as dc
from discord.ext import commands

from globals import conn, cursor
from cogs.cogs_auxiliar import Auxiliar


class Database(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @staticmethod
    def initialize_database():

        cursor.execute(
            """CREATE TABLE guilds
                (name TEXT NOT NULL,
                guild_id INTEGER NOT NULL,
                music_channel_id INTEGER,
                greetings_channel_id INTEGER,
                member_role_id INTEGER)"""
        )
        conn.commit()

    @commands.command()
    async def configmusic(self, ctx, music_channel: dc.TextChannel = None):

        auxiliar = Auxiliar(self.bot)
        if ctx.author.guild_permissions.administrator:

            cursor.execute(
                f"SELECT name FROM sqlite_master WHERE type='table' AND name='guilds'"
            )
            table_exists = cursor.fetchone() is not None

            if not table_exists:
                self.initialize_database()

            cursor.execute(
                f"SELECT guild_id FROM guilds WHERE guild_id = {ctx.guild.id}"
            )
            guild_exists = cursor.fetchone() is not None

            if not guild_exists:
                cursor.execute(
                    "INSERT INTO guilds (name, guild_id) VALUES (?, ?)",
                    (ctx.guild.name, ctx.guild.id),
                )
                conn.commit()

            self.insert_music_channel_id(music_channel)
            await auxiliar.send_embed_message(
                ctx, f"O canal de música foi definido para {music_channel.mention}."
            )

        else:
            await auxiliar.send_embed_message(ctx, "Você não tem permissão para isso!")

    @staticmethod
    def insert_music_channel_id(channel):

        cursor.execute(
            "UPDATE guilds SET music_channel_id = ? WHERE guild_id = ?",
            (channel.id, channel.guild.id),
        )
        conn.commit()

    def read_music_channel_id(self, guild):

        cursor.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='guilds'"
        )
        table_exists = cursor.fetchone() is not None

        if not table_exists:
            self.initialize_database()

        cursor.execute(f"SELECT guild_id FROM guilds WHERE guild_id = {guild.id}")
        guild_exists = cursor.fetchone() is not None

        if not guild_exists:
            cursor.execute(
                "INSERT INTO guilds (name, guild_id) VALUES (?, ?)",
                (guild.name, guild.id),
            )
            conn.commit()

        cursor.execute(
            "SELECT music_channel_id FROM guilds WHERE guild_id = ?", (guild.id,)
        )
        music_channel_id = cursor.fetchone()

        if music_channel_id is None:
            return None

        return music_channel_id[0]

    @commands.command()
    async def configgreetings(self, ctx, greetings_channel: dc.TextChannel = None):

        auxiliar = Auxiliar(self.bot)
        if ctx.author.guild_permissions.administrator:

            cursor.execute(
                f"SELECT name FROM sqlite_master WHERE type='table' AND name='guilds'"
            )
            table_exists = cursor.fetchone() is not None

            if not table_exists:
                self.initialize_database()

            cursor.execute(
                f"SELECT guild_id FROM guilds WHERE guild_id = {ctx.guild.id}"
            )
            guild_exists = cursor.fetchone() is not None

            if not guild_exists:
                cursor.execute(
                    "INSERT INTO guilds (name, guild_id) VALUES (?, ?)",
                    (ctx.guild.name, ctx.guild.id),
                )
                conn.commit()

            self.insert_greetings_channel_id(greetings_channel)
            await auxiliar.send_embed_message(
                ctx,
                f"O canal de boas vindas foi definido para {greetings_channel.mention}.",
            )

        else:
            await auxiliar.send_embed_message(ctx, "Você não tem permissão para isso!")

    @staticmethod
    def insert_greetings_channel_id(channel):

        cursor.execute(
            "UPDATE guilds SET greetings_channel_id = ? WHERE guild_id = ?",
            (channel.id, channel.guild.id),
        )
        conn.commit()

    def read_greetings_channel_id(self, guild):

        cursor.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='guilds'"
        )
        table_exists = cursor.fetchone() is not None

        if not table_exists:
            self.initialize_database()

        cursor.execute(f"SELECT guild_id FROM guilds WHERE guild_id = {guild.id}")
        guild_exists = cursor.fetchone() is not None

        if not guild_exists:
            cursor.execute(
                "INSERT INTO guilds (name, guild_id) VALUES (?, ?)",
                (guild.name, guild.id),
            )
            conn.commit()

        cursor.execute(
            "SELECT greetings_channel_id FROM guilds WHERE guild_id = ?", (guild.id,)
        )
        greetings_channel_id = cursor.fetchone()

        if greetings_channel_id is None:
            return None

        return greetings_channel_id[0]

    @commands.command()
    async def configrole(self, ctx, member_role: dc.Role = None):

        auxiliar = Auxiliar(self.bot)
        if ctx.author.guild_permissions.administrator:

            cursor.execute(
                f"SELECT name FROM sqlite_master WHERE type='table' AND name='guilds'"
            )
            table_exists = cursor.fetchone() is not None

            if not table_exists:
                self.initialize_database()

            cursor.execute(
                f"SELECT guild_id FROM guilds WHERE guild_id = {ctx.guild.id}"
            )
            guild_exists = cursor.fetchone() is not None

            if not guild_exists:
                cursor.execute(
                    "INSERT INTO guilds (name, guild_id) VALUES (?, ?)",
                    (ctx.guild.name, ctx.guild.id),
                )
                conn.commit()

            self.insert_member_role_id(member_role)
            await auxiliar.send_embed_message(
                ctx, f"O cargo de membro foi definido para {member_role.mention}."
            )

        else:
            await auxiliar.send_embed_message(ctx, "Você não tem permissão para isso!")

    @staticmethod
    def insert_member_role_id(role):

        cursor.execute(
            "UPDATE guilds SET member_role_id = ? WHERE guild_id = ?",
            (role.id, role.guild.id),
        )
        conn.commit()

    def read_member_role_id(self, guild):

        cursor.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='guilds'"
        )
        table_exists = cursor.fetchone() is not None

        if not table_exists:
            self.initialize_database()

        cursor.execute(f"SELECT guild_id FROM guilds WHERE guild_id = {guild.id}")
        guild_exists = cursor.fetchone() is not None

        if not guild_exists:
            cursor.execute(
                "INSERT INTO guilds (name, guild_id) VALUES (?, ?)",
                (guild.name, guild.id),
            )
            conn.commit()

        cursor.execute(
            "SELECT member_role_id FROM guilds WHERE guild_id = ?", (guild.id,)
        )
        member_role_id = cursor.fetchone()

        if member_role_id is None:
            return None

        return member_role_id[0]


async def setup(bot):

    await bot.add_cog(Database(bot))
