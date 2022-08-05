import asyncio
import logging
import os
import random
from datetime import datetime, timedelta
import re
from time import sleep

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from web3 import Web3
import aiohttp

from joeBot import JoePic, JoeSubGraph, Constants, Utils
from joeBot.MoneyMakerBot import MoneyMaker
from joeBot.Utils import readable, Ticker


logger = logging.getLogger(__name__)
load_dotenv()
# web3
w3 = Web3(Web3.HTTPProvider("https://api.avax.network/ext/bc/C/rpc"))
if not w3.isConnected():
    raise Exception("Error web3 can't connect")
joetoken_contract = w3.eth.contract(
    address=Constants.JOETOKEN_ADDRESS, abi=Constants.ERC20_ABI
)

MIN_USD_VALUE = 5_000
SLIPPAGE = 100
time_window = 3 * 3_600
ranToday = True
started = False


class MoneyMakerTicker(commands.Cog, Ticker):
    def __init__(self, channels, callConvert):
        self.time_to_wait = 0
        self.channels = channels
        self.callConvert = callConvert

    @tasks.loop(hours=72)
    async def ticker(self):
        await asyncio.sleep(self.time_to_wait)
        try:
            await self.callConvert()

            self.time_to_wait = random.randint(0, time_window)
            await self.channels.get_channel(self.channels.BOT_ERRORS).send(
                "Info: schedule of next buyback : [{}] .".format(
                    (
                        self.ticker.next_iteration
                        + timedelta(seconds=self.time_to_wait)
                    ).strftime("%d/%m/%Y %H:%M:%S")
                )
            )

        except Exception as e:
            await self.channels.get_channel(self.channels.BOT_ERRORS).send(
                "Error on ticker: {}".format(e)
            )

    @ticker.before_loop
    async def before_ticker(self):
        now = datetime.now()
        nextRedistribution = now.replace(hour=20, minute=59, second=59)
        nextRedistribution += timedelta(days=(now.timestamp() // 86400) % 3)
        timeBefore9PM = (nextRedistribution - now).total_seconds()

        if timeBefore9PM < 0:
            timeBefore9PM += 3 * 86_400
            nextRedistribution += timedelta(days=3)

        self.time_to_wait = random.randint(0, time_window)
        await self.channels.get_channel(self.channels.BOT_ERRORS).send(
            "Info: schedule of next buyback : [{}].".format(
                (nextRedistribution + timedelta(seconds=self.time_to_wait)).strftime(
                    "%d/%m/%Y %H:%M:%S"
                )
            )
        )

        await asyncio.sleep(timeBefore9PM)


class JoeTicker(commands.Cog, Ticker):
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(seconds=60)
    async def ticker(self):
        try:
            price = JoeSubGraph.getJoePrice()
            activity = "JOE: ${}".format(round(price, 4))
            await self.bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching, name=activity
                )
            )
        except Exception as e:
            logger.error(e)
            pass


class JoeBot:
    moneyMaker = MoneyMaker
    joePic = JoePic.JoePic()
    discordBot = commands.Bot
    channels = Constants.Channels
    taskManager = Utils.TaskManager

    def __init__(self, discordBot):
        self.discordBot = discordBot
        for server in self.discordBot.guilds:
            self.channels = Constants.Channels(server.id, discordBot)
        self.moneyMaker = MoneyMaker()
        self.taskManager = Utils.TaskManager(
            (
                JoeTicker(self.discordBot),
                MoneyMakerTicker(self.channels, self.callConvert),
            )
        )
        BARN_KEY = os.getenv("BARN_KEY")
        self.auth_header = {"x-joebarn-api-key": BARN_KEY}

    async def onReady(self):
        """starts joeBot"""
        logger.info("joeBot have logged in as {0.user}".format(self.discordBot))
        await self.channels.get_channel(self.channels.BOT_ERRORS).send(
            self.taskManager.start()
        )

    async def about(self, ctx):
        about = JoeSubGraph.getAbout()
        await ctx.send(about)
        return

    async def setMinUsdValueToConvert(self, ctx):
        global MIN_USD_VALUE
        value = ctx.message.content.replace(Constants.SET_MIN_USD_COMMAND, "").strip()
        if value.isdigit():
            MIN_USD_VALUE = int(value)
        await ctx.send("Min usd: ${}".format(readable(MIN_USD_VALUE, 2)))

    async def setSlippageToConvert(self, ctx):
        global SLIPPAGE
        value = ctx.message.content.replace(Constants.SET_SLIPPAGE, "").strip()
        if value.isdigit():
            SLIPPAGE = int(value)
        await ctx.send("Slippage: {}%".format(readable(SLIPPAGE / 100, 2)))

    async def callConvert(self):
        global MIN_USD_VALUE, SLIPPAGE
        try:
            previous_avax_balance = JoeSubGraph.getAvaxBalance(
                Constants.MONEYMAKER_CALLER_ADDRESS
            )
            tx_hashs, error_on_pairs = self.moneyMaker.callConvertMultiple(
                min_usd_value=MIN_USD_VALUE, slippage=SLIPPAGE
            )
            avax_balance = JoeSubGraph.getAvaxBalance(
                Constants.MONEYMAKER_CALLER_ADDRESS
            )

            sleep(10)  # wait 10s to be sure block is confirmed
            list_of_strings = self.moneyMaker.getDailyInfo()

            if list_of_strings[0][:10] != "Total: 0 $":
                await self.sendMessage(list_of_strings, self.channels.BOT_FEED)
            else:
                await self.channels.get_channel(self.channels.BOT_ERRORS).send(
                    "<@198828350473502720> ERROR convert doesn't seem to have occured"
                )

            await self.channels.get_channel(self.channels.BOT_ERRORS).send(
                "Convert() tx_hashs: "
                + " ".join(tx_hashs)
                + "\nAvax Balance: {} (used {})".format(
                    readable(avax_balance, 2),
                    readable(previous_avax_balance - avax_balance, 2),
                )
            )

            if error_on_pairs:
                err = []

                if len(error_on_pairs.keys()) > 1:
                    err.append("<@198828350473502720>")
                for k in error_on_pairs.keys():
                    if k == "local":
                        for e, v in error_on_pairs[k].items():
                            err.append("**({}) {}:**".format(k, e))
                            for info in v:
                                pair, tok0, tok1, sym0, sym1 = info
                                err.append(
                                    "> **{}: {} - {}**\n> *{} - {}*".format(
                                        pair, sym0, sym1, tok0, tok1
                                    )
                                )
                    else:
                        err.append("**{}:**".format(k))
                        for v in error_on_pairs[k].values():
                            err.append("> {}".format(v))

                await self.sendMessage(err, self.channels.BOT_ERRORS)
        except Exception as e:
            messages = ["<@198828350473502720> convert failed with an error", str(e)]
            await self.sendMessage(messages, self.channels.BOT_ERRORS)

    async def joePic(self, ctx):
        """command for personalised profile picture, input a color (RGB or HEX) output a reply with the profile
        picture"""
        if ctx.message.channel.id == self.channels.JOEPIC_CHANNEL_ID:
            try:
                answer = self.joePic.do_profile_picture(
                    ctx.message.content.replace(Constants.PROFILE_PICTURE_COMMAND, "")[
                        1:
                    ]
                )
                await ctx.reply(answer[0], file=answer[1])
            except ValueError:
                e = discord.Embed(
                    title="Error on {} command !".format(
                        Constants.PROFILE_PICTURE_COMMAND[1:]
                    ),
                    description=Constants.ERROR_ON_PROFILE_PICTURE,
                    color=0xF24E4D,
                )
                await ctx.reply(embed=e)
        return

    async def onCommandError(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            if ctx.message.channel.id == self.channels.JOEPIC_CHANNEL_ID:
                e = discord.Embed(
                    title="Error on {} command !".format(
                        Constants.PROFILE_PICTURE_COMMAND[1:]
                    ),
                    description=Constants.ERROR_ON_PROFILE_PICTURE,
                    color=0xF24E4D,
                )
                await ctx.reply(embed=e)
            return
        raise error

    async def sendMessage(self, list_of_strings, channel_id=None):
        if channel_id is None:
            channel_id = self.channels.BOT_ERRORS
        message, length = [], 0
        channel = self.channels.get_channel(channel_id)
        for string in list_of_strings:
            length += len(string) + 2
            if length > 1800:
                await channel.send("\n".join(message))
                message, length = [], len(string) + 2
            message.append(string)
        if message:
            await channel.send("\n".join(message))

    async def blocklist(self, ctx):
        if ctx.message.channel.id != self.channels.FAKE_COLLECTIONS_CHANNEL_ID:
            """command usable only in FAKE_COLLECTIONS_CHANNEL_ID"""
            return

        if ctx.message.reference:
            """mod is replying to reporting user - fetch user's message"""
            message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        else:
            """mod is providing collection address himself - fetch his message"""
            message = ctx.message

        found_addresses = self.find_address(message.content)

        if not found_addresses:
            await ctx.reply("Collection address not found in your message.")
        elif len(found_addresses) != 1:
            await ctx.reply(
                f"Please provide only one collection address at the time. "
                f"Found {len(found_addresses)} addresses in your message."
            )
        else:
            verification_status = await self.verification_status(found_addresses[0])
            if not verification_status:
                await ctx.reply(f"Collection {found_addresses[0]} doesn't exist")
                return
            elif verification_status in Constants.VERIFIED:
                await ctx.reply("You cannot blocklist verified collection")
                return
            else:
                await self.blocklist_collection(ctx, found_addresses[0], message)

    def find_address(self, msg):
        address_regex = re.compile(r"0x[a-fA-F0-9]{40}")
        address = re.findall(address_regex, msg)
        if address:
            return address

    async def verification_status(self, address):
        url = f"{Constants.ENV_URL}v2/collections/{address}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.auth_header) as response:
                verified_status = await response.json()

        if response.status == 200:
            return verified_status["verified"]
        elif response.status == 404:
            return ""
        else:
            raise Exception("Status code of verification_status not in [200, 404]")

    async def blocklist_collection(self, ctx, address, report):
        blocklist_url = f"{Constants.ENV_URL}v2/admin/blocklist-collections"
        payload = {"blocklistAddrs": [address]}
        async with aiohttp.ClientSession() as session:
            async with session.post(
                blocklist_url, headers=self.auth_header, json=payload
            ) as response:
                json_response = await response.json()
        if json_response == []:
            await ctx.reply(
                f"Tried blocklisting {address}, but it's probably blocklisted already. "
                f"Thanks for reporting {report.author.mention} anyway!"
            )
        elif json_response[0]["verificationStatus"] == "blocklisted":
            logger.info(
                "Collection {} blocklisted by {}, reported by {}".format(
                    address,
                    ctx.message.author.name,
                    report.author.name,
                )
            )
            await ctx.reply(
                f"Found collection address {address} and blocklisted it. "
                f"Thanks for reporting {report.author.mention}"
            )
        else:
            await ctx.reply(
                f"Tried blocklisting {address} and it failed. "
                f"Thanks for reporting {report.author.mention} anyway"
            )

    async def allowlist(self, ctx):
        if ctx.message.channel.id != self.channels.FAKE_COLLECTIONS_CHANNEL_ID:
            """command usable only in FAKE_COLLECTIONS_CHANNEL_ID"""
            return

        if ctx.message.reference:
            """mod is replying to reporting user - fetch user's message"""
            message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        else:
            """mod is providing collection address himself - fetch his message"""
            message = ctx.message

        found_addresses = self.find_address(message.content)

        if not found_addresses:
            await ctx.reply("Collection address not found in your message.")
        elif len(found_addresses) != 1:
            await ctx.reply(
                f"Please provide only one collection address at the time. "
                f"Found {len(found_addresses)} addresses in your message."
            )
        else:
            verification_status = await self.verification_status(found_addresses[0])
            if not verification_status:
                await ctx.reply(f"Collection {found_addresses[0]} doesn't exist")
                return
            elif verification_status in Constants.VERIFIED:
                await ctx.reply("You cannot allowilist verified collection")
                return
            else:
                await self.allowlist_collection(ctx, found_addresses[0], message)

    async def allowlist_collection(self, ctx, address, report):
        allowlist_url = f"{Constants.ENV_URL}v2/admin/blocklist-collections"
        payload = {"allowlistAddrs": [address]}
        async with aiohttp.ClientSession() as session:
            async with session.post(
                allowlist_url, headers=self.auth_header, json=payload
            ) as response:
                json_response = await response.json()
        if json_response == []:
            await ctx.reply(
                f"Tried allowlisting {address}, but it's probably allowlisted already. "
                f"Thanks for reporting {report.author.mention} anyway!"
            )
        elif json_response[0]["verificationStatus"] == "unverified":
            logger.info(
                "Collection {} allowlisted by {}, reported by {}".format(
                    address,
                    ctx.message.author.name,
                    report.author.name,
                )
            )
            await ctx.reply(
                f"Found collection address {address} and allowlisted it. "
                f"Thanks for reporting {report.author.mention}"
            )
        else:
            await ctx.reply(
                f"Tried allowlisting {address} and it failed. "
                f"Thanks for reporting {report.author.mention} anyway"
            )
