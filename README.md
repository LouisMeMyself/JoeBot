# [JoeBot](https://github.com/LouisMeMyself/joebot)

A small bot to create profile picture using Joe logo and get informations about the token.

Works for Discord and Telegram.

Installation
-------

### Use Virtualenv

This repo uses virtualenv

Installation of the dependencies required for the project:
```bash
# activation of the virtual environment
... $> source venv/bin/activate

# installation of dependencies (only after having activated the virtual environment!)
(venv) ... $> pip install -r requirements.txt
```

Don't forget to add your keys (Wallet private key, discord API and Telegram API keys):
```bash
# Create a .env file
(venv) ... $> cp .env.example .env
# Add your keys
(venv) ... $> nano .env
```


Then, to launch the bot simply type:
```bash
# start the discord bot
(venv) ... $> python main.py
# start the telegram bot
(venv) ... $> python JoeTelegramBot.py
```