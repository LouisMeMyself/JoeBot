import json

# Server
TEST_SERVER_ID = 852632556137611334
LIVE_SERVER_ID = 830990443457806347

# Emojis
EMOJI_CHECK = "✅"
EMOJI_CROSS = "❌"
EMOJI_ACCEPT_GUIDELINES = "✅"

# utils
E18 = 10 ** 18

# Commands
COMMAND_BEARD = "beard"
PROFILE_PICTURE_COMMAND = "!joepic"

# Roles
ROLE_FOR_CMD = "Bot Master"
VERIFIED_USER_ROLE = "Joe"

# SubGraph links
JOE_EXCHANGE_SG_URL = "https://api.thegraph.com/subgraphs/name/traderjoe-xyz/exchange"
JOE_BAR_SG_URL = "https://api.thegraph.com/subgraphs/name/traderjoe-xyz/bar"
JOE_DEXCANDLES_SG_URL = "https://api.thegraph.com/subgraphs/name/traderjoe-xyz/dexcandles"
JOE_MAKER_SG_URL = "https://api.thegraph.com/subgraphs/name/traderjoe-xyz/maker"
JOE_MAKERV2_SG_URL = "https://api.thegraph.com/subgraphs/name/traderjoe-xyz/makerv2"

# address for web3
AVAX_RPC = "https://api.avax.network/ext/bc/C/rpc"
JOETOKEN_ADDRESS = "0x6e84a6216eA6dACC71eE8E6b0a5B7322EEbC0fDd"
WAVAX_ADDRESS = "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"
USDTe_ADDRESS = "0xc7198437980c041c805A1EDcbA50c1Ce5db95118"
USDCe_ADDRESS = "0xA7D7079b0FEaD91F3e65f86E8915Cb59c1a4C664"

JOEBAR_ADDRESS = "0x57319d41F71E81F3c65F2a47CA4e001EbAFd4F33"
JOEFACTORY_ADDRESS = "0x9Ad6C38BE94206cA50bb0d90783181662f0Cfa10"
JOEMAKER_ADDRESS = "0x861726BFE27931A4E22a7277bDe6cb8432b65856"
JOEMAKERV2_ADDRESS = "0xC98C3C547DDbcc0029F38E0383C645C202aD663d"

JOEUSDTE_ADDRESS = "0x1643de2efB8e35374D796297a9f95f64C082a8ce"
JOEWAVAX_ADDRESS = "0x454E67025631C065d3cFAD6d71E6892f74487a15"
WAVAXUSDCE_ADDRESS = "0xA389f9430876455C36478DeEa9769B7Ca4E3DDB1"
WAVAXUSDTE_ADDRESS = "0xeD8CBD9F0cE3C6986b22002F03c6475CEb7a6256"

# ABI for web3
try:
    with open("content/abis/erc20tokenabi.json", "r") as f:
        ERC20_ABI = json.load(f)
except FileNotFoundError:
    with open("../content/abis/erc20tokenabi.json", "r") as f:
        ERC20_ABI = json.load(f)

try:
    with open("content/abis/joefactoryabi.json", "r") as f:
        JOEFACTORY_ABI = json.load(f)
except FileNotFoundError:
    with open("../content/abis/joefactoryabi.json", "r") as f:
        JOEFACTORY_ABI = json.load(f)

try:
    with open("content/abis/joemakerabi.json", "r") as f:
        JOEMAKER_ABI = json.load(f)
except FileNotFoundError:
    with open("../content/abis/joemakerabi.json", "r") as f:
        JOEMAKER_ABI = json.load(f)

# assets address
NAME2ADDRESS = {}

# joe ticker
JOE_TICKER = {}

# Errors
ERROR_ON_PROFILE_PICTURE = """How to use joeBot for profile pictures:

1. Choose a HEX color or a RGB color in this format: `#00FFFF`. [(color picker)](https://htmlcolorcodes.com/color-picker/)

2. Enter this command `!joepic [color]` for the color of the jacket and `!joepic [color] [color]` for the color of the jacket and the skin with your selected color(s).
   Add `beard [color]` at the end of the command to also change the color of the beard!

3. Save image + add as your Discord profile photo !"""

ERROR_ON_PROFILE_PICTURE_TG = """How to use /joepic for profile pictures:
1. Choose a HEX color or a RGB color in this format: `#00FFFF`. [(color picker)](https://htmlcolorcodes.com/color-picker/)
2. Enter this command `/joepic [color]` for the color of the jacket and `/joepic [color] [color]` for the color of the jacket and the skin with your selected color(s).
   Add `beard [color]` at the end of the command to also change the color of the beard!"""

# help
HELP_TG = """JoeBot commands:
/price : return the current price of $Joe.
/about : return the current price of $Joe, the market cap, the circulating supply and the total value locked.
/joepic : return a personnalised 3D Joe, (for more help, type /joepic).
/tokenomics : return TraderJoe's tokenomics page.
/contracts : return TraderJoe's contracts page.
/docs : return TraderJoe's docs page.
/discord : return TraderJoe's discord.
/twitter : return TraderJoe's twitter.
/website : return TraderJoe's website.
"""


class Channels:
    def __init__(self, server_id, bot):
        if server_id == LIVE_SERVER_ID:
            server_nb = 0
        elif server_id == TEST_SERVER_ID:
            server_nb = 1
        else:
            raise ValueError

        self.__channel = {}
        for server in bot.guilds:
            if server.id == server_id:
                for channel in server.channels:
                    self.__channel[channel.id] = channel

        self.JOEPIC_CHANNEL_ID = (852663823982788678, 852632612451123221)[server_nb]  # "👨🏻-profile-pictures"
        self.SUGGESTION_CHANNEL_ID = (843655526906593380, 852632695522459709)[server_nb]  # "👨🏻-profile-pictures"
        self.GUIDELINES_CHANNEL_ID = (830990443910529047, 852636664869158912)[
            server_nb]  # "📚-guidelines-and-resources"
        self.COMMAND_CHANNEL_ID = (852658830987100190, 853397123713204244)[server_nb]  # "🤖-bot-commands"
        self.GUIDELINES_MSG_ID = (843668142764589076, 852636768788021288)[server_nb]
        self.BOT_FEED = (898964756508065852, 853397123713204244)[server_nb]

    def get_channel(self, channel_id):
        return self.__channel[channel_id]
