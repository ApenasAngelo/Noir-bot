import os
from dotenv import load_dotenv

import discord as dc
from discord.ext import commands
from cogwatch import watch

import wavelink as wl
from wavelink.ext import spotify

#INICIALIZAÇÃO DO BOT
load_dotenv()
class Bot(commands.Bot):

    def __init__(self) -> None:
        intents = dc.Intents.all()
        intents.message_content = True

        activity = dc.Activity(type=dc.ActivityType.listening, name="vozes...")
        status = dc.Status.do_not_disturb

        super().__init__(intents=intents, command_prefix=os.getenv('prefix'), activity=activity, status=status)

    @watch(path='cogs', preload=True)
    async def on_ready(self) -> None:
        print('O bot está ON!'.format(bot))

    async def setup_hook(self) -> None:
        sc = spotify.SpotifyClient(
            client_id=os.getenv('spotify.ClientID'),
            client_secret=os.getenv('spotify.ClientSecret')
        )

        node: wl.Node = wl.Node(uri=os.getenv('wl.URI'), password=os.getenv('wl.PASSWORD'), secure=True)
        await wl.NodePool.connect(client=self, nodes=[node], spotify=sc)

bot = Bot()


async def loadcogs():

    for filename in os.listdir('./cogs'):
        if filename.startswith('cogs_'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            print(f"Loaded Cog: {filename[:-3]}")


#TOKEN
bot.run(os.getenv('dc.TOKEN'))