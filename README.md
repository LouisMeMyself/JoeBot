# [JoeBot](https://github.com/traderjoe-xyz/joe-bot)

A small bot to create profile picture using Joe logo and get informations about the token.

Works for Discord and Telegram.

## Installation

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

NOTE:
On mac, it may fail. If it does try to install package one by one and for `cairo`use this:

```bash
(venv) ... $> brew install cairo libxml2 libxslt libffi
(venv) ... $> pip3 install cairosvg
```


## Blocklist/allowlist

Is response {'verificationStatus': 'unverified'} from /v2/admin/blocklist-collections enough to confirm, that collection is blocklisted? Or should there be another API call to confirm it? On https://barn-dev.joepegs.app/ confirmation from v2/collections/{address} endpoint takes around 45 seconds


Usage:

`!blocklist collection-address`

Or `!blocklist` while reponding to someone, that provided `collection-address`.

There can be only 1 `collection-address` in message, but other characters are ok. for example responding to message: 
```
help https://joepegs.com/collections/0x2cd4dbcbfc005f8096c22579585fb91097d8d259 is fake
``` 
will work (but will not block collection, because it's verified)

There is also `!allowlist` command, that will restore `blocklisted` collection to `unverified` status.

Both of these comands:
1) Work only in `#fake-collections` channel
2) Work only when used by user with `Community Management` role
3) Will not block/unblock verified collections
4) Will not take effect if more than 1 address is found 
5) Will not take any effect when used outside `#fake-collections` channel or by user without `Community Management` role
6) Will prioritize content of message that mod replies to.

