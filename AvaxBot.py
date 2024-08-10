import logging
import os

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

from joeBot import JoeSubGraph
from joeBot import JoeBarn
from joeBot.Utils import TaskManager, Ticker


load_dotenv()

logger = logging.getLogger(__name__)

# Discord
discord_bot = commands.Bot(command_prefix="./.")


class AvaxTicker(commands.Cog, Ticker):
    def __init__(self):
        self.carousel = True

    def start(self):
        self.ticker.start()

    @tasks.loop(seconds=10)
    async def ticker(self):
        try:
            if self.carousel:
                (avaxPrice, _) = JoeBarn.get_avax_price()
                activity = "AVAX: ${}".format(round(avaxPrice, 2))
                self.carousel = False
            else:
                gasPrice = JoeSubGraph.getCurrentGasPrice()
                activity = "GAS PRICE: {}".format(round(gasPrice / 10**9))
                self.carousel = True
            await discord_bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching, name=activity
                )
            )
        except Exception as e:
            logger.error(e)
            pass


@discord_bot.event
async def on_ready():
    """starts AVAX ticker"""
    logger.info("joeBot have logged in as {0.user}".format(discord_bot))
    TaskManager((AvaxTicker(),)).start()


@discord_bot.event
async def on_command_error(ctx, error):
    return


def start():
    discord_bot.run(os.getenv("DISCORD_AVAXBOT_KEY"))


if __name__ == "__main__":
    # Discord
    discord_bot.run(os.getenv("DISCORD_AVAXBOT_KEY"))
