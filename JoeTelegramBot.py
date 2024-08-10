import asyncio
import datetime
import logging
import time
import os

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from dotenv import load_dotenv
from web3 import Web3

from joeBot import JoeBarn, Constants
from joeBot.Utils import smartRounding
from dotenv import load_dotenv

# Env
load_dotenv()


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=os.getenv("TELEGRAM_JOEBOT_KEY"))

dp = Dispatcher()

SWAP_LINK = "[Swap](https://traderjoexyz.com/avalanche/trade?utm_source=telegram&utm_medium=command&utm_campaign=joebotprompt)"


# safeguard to not spam
class Timer:
    def __init__(self):
        self.last_msg_time = {}

    def canMessageOnChatId(self, chat_id, cd_in_s=5):
        if chat_id not in self.last_msg_time:
            self.last_msg_time[chat_id] = 0
        if self.last_msg_time[chat_id] + cd_in_s > time.time():
            return False
        else:
            self.last_msg_time[chat_id] = time.time()
            return True


timer = Timer()
time_between_updates = 60
last_reload = None


@dp.message(Command("startticker"))
async def startTicker(message: types.Message):
    """start joeticker"""
    if not timer.canMessageOnChatId(message.chat.id):
        return

    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if not member.status == "administrator" and not member.status == "creator":
        await bot.send_message(
            message.chat.id,
            "You're not admin, you can't use that command.",
            message_thread_id=message.message_thread_id,
        )
        return

    if (
        message.reply_to_message is not None
        and message.reply_to_message.from_user.id == bot.id
    ):
        Constants.JOE_TICKER[message.chat.id] = message.reply_to_message.message_id
        await joeTicker(message.chat.id, message.reply_to_message.message_id)
        await bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id)

    else:
        mess_id = (
            await bot.send_message(
                message.chat.id,
                "JOE price is $X",
                message_thread_id=message.message_thread_id,
            )
        ).message_id
        Constants.JOE_TICKER[message.chat.id] = mess_id
        await bot.pin_chat_message(message.chat.id, mess_id)
        await joeTicker(message.chat.id, mess_id)


@dp.message(Command("stopticker"))
async def stopTicker(message: types.Message):
    """stop joeTicker"""
    if not timer.canMessageOnChatId(message.chat.id):
        return
    chat_id = message.chat.id
    member = await bot.get_chat_member(chat_id, message.from_user.id)
    if not member.status == "administrator" and not member.status == "creator":
        return
    if message.chat.id in Constants.JOE_TICKER:
        await bot.send_message(
            chat_id,
            "JoeTicker stopped.",
            message_thread_id=message.message_thread_id,
        )
        await bot.delete_message(chat_id, Constants.JOE_TICKER[chat_id])
        Constants.JOE_TICKER.pop(chat_id)

    elif (
        message.reply_to_message is not None
        and message.reply_to_message.from_user.id == bot.id
    ):
        mid = message.reply_to_message.message_id
        try:
            await bot.send_message(
                chat_id,
                "JoeTicker stopped.",
                message_thread_id=message.message_thread_id,
            )
            await bot.delete_message(chat_id, mid)
        except:
            pass
    else:
        await bot.send_message(
            chat_id,
            "JoeTicker not started.",
            message_thread_id=message.message_thread_id,
        )


async def joeTicker(chat_id, mess_id):
    global last_reload
    mess = "JOE price is $X"
    while chat_id in Constants.JOE_TICKER and Constants.JOE_TICKER[chat_id] == mess_id:
        try:
            logger.info("joeTicker is up")
            while (
                chat_id in Constants.JOE_TICKER
                and Constants.JOE_TICKER[chat_id] == mess_id
            ):
                (price, _) = JoeBarn.get_joe_price()
                new_mess = "JOE price is ${} (updated at {} UTC)".format(
                    round(price, 4), datetime.datetime.utcnow().strftime("%H:%M:%S")
                )
                if new_mess != mess:
                    mess = new_mess
                    await bot.edit_message_text(mess, chat_id, mess_id)

                await asyncio.sleep(time_between_updates)
        except ConnectionError:
            logger.error("Connection error, retrying in 60 seconds...")
        except AssertionError:
            logger.error("Assertion Error, retrying in 60 seconds...")
        except KeyboardInterrupt:
            logging.info(KeyboardInterrupt)
            break
        except:
            pass
        await asyncio.sleep(time_between_updates)
    return


@dp.message(Command("price"))
async def price(message: types.Message):
    """return the current price of $Joe or $Avax"""
    if not timer.canMessageOnChatId(message.chat.id):
        return
    msg = message.text.lower().replace("/price", "").replace(" ", "")
    if msg != "" and msg != "joe":
        if msg == "avax":
            (avaxp, _) = JoeBarn.get_avax_price()
            await bot.send_message(
                message.chat.id,
                "${} : ${}\n{}".format(msg.upper(), smartRounding(avaxp), SWAP_LINK),
                message_thread_id=message.message_thread_id,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
            )
            return

    (priceUsd, priceNative) = JoeBarn.get_joe_price()

    await bot.send_message(
        message.chat.id,
        "$JOE: ${}\n{} $JOE/$AVAX\n{}".format(
            smartRounding(priceUsd, 4), smartRounding(1 / priceNative, 4), SWAP_LINK
        ),
        message_thread_id=message.message_thread_id,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
    )


async def main():
    print(os.getenv("TELEGRAM_JOEBOT_KEY"))
    bot = Bot(token=os.getenv("TELEGRAM_JOEBOT_KEY"))
    await dp.start_polling(bot)


def start():
    asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())
