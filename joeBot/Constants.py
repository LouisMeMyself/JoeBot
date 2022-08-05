import json

# Server
TEST_SERVER_ID = 852632556137611334
LIVE_SERVER_ID = 830990443457806347

# Emojis
EMOJI_CHECK = "✅"
EMOJI_CROSS = "❌"
EMOJI_ACCEPT_GUIDELINES = "✅"

# utils
E18 = 10**18
PREMIUM_PER_TRANSACTION = 0.1

# Commands
COMMAND_BEARD = "beard"
PROFILE_PICTURE_COMMAND = "!joepic"
SET_MIN_USD_COMMAND = "!setmin"
SET_SLIPPAGE = "!setslippage"
CONVERT_COMMAND = "!convert"

# Roles
ROLE_FOR_CMD = "Bot Master"
VERIFIED_USER_ROLE = "Joe"

# SubGraph links
JOE_EXCHANGE_SG_URL = "https://api.thegraph.com/subgraphs/name/traderjoe-xyz/exchange"
JOE_BAR_SG_URL = "https://api.thegraph.com/subgraphs/name/traderjoe-xyz/bar"
JOE_DEXCANDLES_SG_URL = (
    "https://api.thegraph.com/subgraphs/name/traderjoe-xyz/dexcandles"
)

# address for web3
AVAX_RPC = "https://api.avax.network/ext/bc/C/rpc"
JOETOKEN_ADDRESS = "0x6e84a6216eA6dACC71eE8E6b0a5B7322EEbC0fDd"
JXJOETOKEN_ADDRESS = "0xc146783a59807154f92084f9243eb139d58da696"
WAVAX_ADDRESS = "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"
USDTe_ADDRESS = "0xc7198437980c041c805A1EDcbA50c1Ce5db95118"
USDCe_ADDRESS = "0xA7D7079b0FEaD91F3e65f86E8915Cb59c1a4C664"
ZERO_ADDRESS_256 = "0x0000000000000000000000000000000000000000000000000000000000000000"

JOEBAR_ADDRESS = "0x57319d41F71E81F3c65F2a47CA4e001EbAFd4F33"
RJOE_ADDRESS = "0x102D195C3eE8BF8A9A89d63FB3659432d3174d81"
STABLEJOESTAKING_ADDRESS = "0x1a731B2299E22FbAC282E7094EdA41046343Cb51"
JOEFACTORY_ADDRESS = "0x9Ad6C38BE94206cA50bb0d90783181662f0Cfa10"
MONEYMAKER_ADDRESS = "0x63C0CF90aE12190B388F9914531369aC1e4e4e47"
MONEYMAKER_CALLER_ADDRESS = "0x65a8cbbf9bc23bcb1c9d1d3039b5bbd9101e6b7a"

JOEUSDTE_ADDRESS = "0x1643de2efB8e35374D796297a9f95f64C082a8ce"
JOEWAVAX_ADDRESS = "0x454E67025631C065d3cFAD6d71E6892f74487a15"
WAVAXUSDCE_ADDRESS = "0xA389f9430876455C36478DeEa9769B7Ca4E3DDB1"
WAVAXUSDTE_ADDRESS = "0xeD8CBD9F0cE3C6986b22002F03c6475CEb7a6256"

# ABI for web3
try:
    with open("content/abis/pairabi.json", "r") as f:
        PAIR_ABI = json.load(f)
except FileNotFoundError:
    with open("../content/abis/pairabi.json", "r") as f:
        PAIR_ABI = json.load(f)

try:
    with open("content/abis/erc20tokenabi.json", "r") as f:
        ERC20_ABI = json.load(f)
except FileNotFoundError:
    with open("../content/abis/erc20tokenabi.json", "r") as f:
        ERC20_ABI = json.load(f)

try:
    with open("content/abis/jcollateralcaperc20delegatorabi.json", "r") as f:
        JCOLLATERAL_ABI = json.load(f)
except FileNotFoundError:
    with open("../content/abis/jcollateralcaperc20delegatorabi.json", "r") as f:
        JCOLLATERAL_ABI = json.load(f)

try:
    with open("content/abis/joefactoryabi.json", "r") as f:
        JOEFACTORY_ABI = json.load(f)
except FileNotFoundError:
    with open("../content/abis/joefactoryabi.json", "r") as f:
        JOEFACTORY_ABI = json.load(f)

try:
    with open("content/abis/moneymakerabi.json", "r") as f:
        MONEYMAKER_ABI = json.load(f)
except FileNotFoundError:
    with open("../content/abis/moneymakerabi.json", "r") as f:
        MONEYMAKER_ABI = json.load(f)

# assets address
symbol_to_address = {}

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
/price <token> : return the current price of token, can be an address or its symbol. default: JOE.
/chart <token> : return the current chart of token, can be an address or its symbol. default: JOE.
/address <token> : return the address of token symbol.
/about : return info about TraderJoe ecosystem.
/leding : return info aobut BankerJoe.
/joepic : return a personnalised 3D Joe, (for more help, type /joepic).
/pricelist : returns the list of tokens that JoeBot can interact with.
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

        self.JOEPIC_CHANNEL_ID = (852663823982788678, 852632612451123221)[
            server_nb
        ]  # "👨🏻-profile-pictures"
        self.SUGGESTION_CHANNEL_ID = (843655526906593380, 852632695522459709)[
            server_nb
        ]  # "👨🏻-profile-pictures"
        self.GUIDELINES_CHANNEL_ID = (830990443910529047, 852636664869158912)[
            server_nb
        ]  # "📚-guidelines-and-resources"
        self.COMMAND_CHANNEL_ID = (852658830987100190, 853397123713204244)[
            server_nb
        ]  # "🤖-bot-commands"
        self.GUIDELINES_MSG_ID = (843668142764589076, 852636768788021288)[server_nb]
        self.BOT_FEED = (898964756508065852, 853397123713204244)[server_nb]
        self.BOT_ERRORS = (909093515634561106, 853397123713204244)[server_nb]

    def get_channel(self, channel_id):
        return self.__channel[channel_id]
