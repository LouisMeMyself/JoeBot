#!/usr/bin/env python3

import logging
import os

from dotenv import load_dotenv


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def main(bot_name):
    if not bot_name:
        raise ValueError(f"Unknown bot name {bot_name}")
    bot_name = bot_name.lower().strip()
    logger.info(f"Running {bot_name}")
    # use local imports to avoid creating bots when importing modules
    if bot_name == "discord-avax":
        import AvaxBot

        AvaxBot.start()
    elif bot_name == "discord-joe":
        import JoeDiscordBot

        JoeDiscordBot.start()
    elif bot_name == "telegram-joe":
        import JoeTelegramBot

        JoeTelegramBot.start()
    else:
        raise ValueError(f"Unknown bot name {bot_name}")


if __name__ == "__main__":
    load_dotenv()
    bot_name = os.getenv("BOT_NAME")
    main(bot_name)
