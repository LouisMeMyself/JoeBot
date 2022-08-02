import datetime
import json
import logging
from pathlib import Path

import pandas as pd
import requests
from web3 import Web3
from web3.middleware import geth_poa_middleware

from joeBot import Constants
from joeBot.Constants import E18
from joeBot.Utils import readable, smartRounding


logger = logging.getLogger(__name__)

# web3
w3 = Web3(Web3.HTTPProvider(Constants.AVAX_RPC))
if not w3.isConnected():
    raise Exception("Error web3 can't connect")
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

joetoken_contract = w3.eth.contract(
    address=w3.toChecksumAddress(Constants.JOETOKEN_ADDRESS), abi=Constants.ERC20_ABI
)
jxjoetoken_contract = w3.eth.contract(
    address=w3.toChecksumAddress(Constants.JXJOETOKEN_ADDRESS),
    abi=Constants.JCOLLATERAL_ABI,
)


def genericQuery(query, sg_url=Constants.JOE_EXCHANGE_SG_URL):
    r = requests.post(sg_url, json={"query": query})
    assert r.status_code == 200
    return json.loads(r.text)


def getPriceOf(tokenAddress):
    r = requests.get("https://api.traderjoexyz.com/priceusd/{}".format(tokenAddress))
    assert r.status_code == 200
    return json.loads(r.text)


def getDerivedPriceOf(tokenAddress):
    r = requests.get("https://api.traderjoexyz.com/priceavax/{}".format(tokenAddress))
    assert r.status_code == 200
    return json.loads(r.text)


def getCirculatingSupply():
    r = requests.get("https://api.traderjoexyz.com/supply/circulating")
    assert r.status_code == 200
    return json.loads(r.text)


def getLendingTotalSupply():
    r = requests.get("https://api.traderjoexyz.com/lending/supply")
    assert r.status_code == 200
    return json.loads(r.text)


def getLendingTotalBorrow():
    r = requests.get("https://api.traderjoexyz.com/lending/borrow")
    assert r.status_code == 200
    return json.loads(r.text)


def getTokenCandles(token_address, period, nb):
    if token_address < Constants.WAVAX_ADDRESS:
        token0, token1 = token_address, Constants.WAVAX_ADDRESS
        isTokenPerAvax = False
    elif token_address > Constants.WAVAX_ADDRESS:
        token0, token1 = Constants.WAVAX_ADDRESS, token_address
        isTokenPerAvax = True
    else:
        # Token is avax
        token0, token1 = Constants.WAVAX_ADDRESS, Constants.USDTe_ADDRESS
        isTokenPerAvax = False

    query = genericQuery(
        "{candles(first:"
        + nb
        + ', orderBy: time, orderDirection: desc, \
    where: {token0: "'
        + token0
        + '", token1: "'
        + token1
        + '",\
      period: '
        + period
        + "}) {time, open, high, low, close}}",
        Constants.JOE_DEXCANDLES_SG_URL,
    )
    query["isTokenPerAvax"] = token0 == Constants.WAVAX_ADDRESS

    data_df = pd.DataFrame(query["data"]["candles"])

    data_df["date"] = data_df["time"].apply(
        lambda x: datetime.datetime.utcfromtimestamp(x)
    )
    data_df = data_df.set_index("date")

    if not isTokenPerAvax:
        data_df[["open", "close", "high", "low"]] = data_df[
            ["open", "close", "high", "low"]
        ].applymap(lambda x: 1 / float(x))
    else:
        data_df[["open", "close", "high", "low"]] = data_df[
            ["open", "close", "high", "low"]
        ].applymap(lambda x: float(x))
    return data_df


def getCurrentGasPrice(nb=50):
    """
    get current gas price, weighted by most recents one
    """
    block_number = w3.eth.get_block_number()
    weighted_sum = sum(
        [
            w3.eth.getBlock(n).baseFeePerGas * (n + nb - block_number)
            for n in range(block_number, block_number - nb, -1)
        ]
    )
    # sum([60, 59, ... , 1]) == 61 * 60 / 2
    return int(weighted_sum / (nb * (nb - 1) / 2))


def getMoneyMakerPositions(
    min_usd_value, money_maker_address=None, return_reserve_and_balance=False
):
    """
    getMoneyMakerPositions return the position of MoneyMaker that are worth more than min_usd_value
    and if he owns less than half the lp.

    :param min_usd_value: The min USD value to be actually returned.
    :param money_maker_address: address of MoneyMaker, default: V3.
    :param return_reserve_and_balance: boolean value to return or not the reserves and balances (in usd),
                                       default: False.
    :return: 2 lists, the first one is the list of the token0 of the pairs that satisfied the requirements
    the second one is the same thing but for token1.
    """
    last_id, query_exchange = "", {}
    tokens0, tokens1 = [], []
    symbols0, symbols1 = [], []
    pairs = []
    pairs_reserve_usd, mm_balance_usd = [], []
    if money_maker_address is None:
        money_maker_address = Constants.MONEYMAKER_ADDRESS.lower()
    else:
        money_maker_address = money_maker_address.lower()
    while last_id == "" or len(query_exchange["data"]["liquidityPositions"]) == 1000:
        query_exchange = genericQuery(
            '{liquidityPositions(first: 1000, where: {id_gt: "'
            + last_id
            + '", user: "'
            + money_maker_address
            + '"}) '
            "{id, liquidityTokenBalance, "
            "pair { token0{id, symbol}, token1{id, symbol}, reserveUSD, totalSupply}}}"
        )
        for liquidity_position in query_exchange["data"]["liquidityPositions"]:
            pair = liquidity_position["pair"]

            money_maker_balance = float(liquidity_position["liquidityTokenBalance"])
            pair_total_supply = float(pair["totalSupply"])
            if pair_total_supply == 0:
                continue
            pair_reserve_usd = float(pair["reserveUSD"])
            money_maker_balance_usd = (
                money_maker_balance / pair_total_supply * pair_reserve_usd
            )

            if (
                money_maker_balance_usd > min_usd_value
                and money_maker_balance / pair_total_supply < 0.49
            ):
                tokens0.append(pair["token0"]["id"])
                tokens1.append(pair["token1"]["id"])
                pairs.append(liquidity_position["id"][:42])
                symbols0.append(pair["token0"]["symbol"])
                symbols1.append(pair["token1"]["symbol"])
                pairs_reserve_usd.append(pair_reserve_usd)
                mm_balance_usd.append(money_maker_balance_usd)
        last_id = query_exchange["data"]["liquidityPositions"][-1]["id"]
    if return_reserve_and_balance:
        return (
            pairs,
            tokens0,
            tokens1,
            symbols0,
            symbols1,
            pairs_reserve_usd,
            mm_balance_usd,
        )
    return pairs, tokens0, tokens1, symbols0, symbols1


# Using API
def getAvaxPrice():
    return getPriceOf(Constants.WAVAX_ADDRESS) / E18


def getAvaxBalance(address):
    return round(float(w3.eth.getBalance(w3.toChecksumAddress(address))) / 1e18, 3)


# Using API
def getJoePrice():
    return getPriceOf(Constants.JOETOKEN_ADDRESS) / E18


def getTraderJoeTVL():
    JoeHeldInLending = float(
        w3.fromWei(jxjoetoken_contract.functions.getCash().call(), "ether")
    )
    JoeHeldInJoeBar = float(
        w3.fromWei(
            joetoken_contract.functions.balanceOf(Constants.JOEBAR_ADDRESS).call(),
            "ether",
        )
    )
    JoeStakedInRJoe = float(
        w3.fromWei(
            joetoken_contract.functions.balanceOf(Constants.RJOE_ADDRESS).call(),
            "ether",
        )
    )
    JoeStakedInStableJoe = float(
        w3.fromWei(
            joetoken_contract.functions.balanceOf(
                Constants.STABLEJOESTAKING_ADDRESS
            ).call(),
            "ether",
        )
    )
    joePrice = float(getJoePrice())

    sum_ = (
        JoeHeldInJoeBar - JoeHeldInLending + JoeStakedInRJoe + JoeStakedInStableJoe
    ) * joePrice

    last_id, queryExchange = "", {}
    while last_id == "" or len(queryExchange["data"]["pairs"]) == 1000:
        queryExchange = genericQuery(
            '{pairs(first: 1000, where: {id_gt: "'
            + last_id
            + '"}){id, reserveUSD, volumeUSD}}'
        )
        for pair in queryExchange["data"]["pairs"]:
            reserveUSD = float(pair["reserveUSD"])
            # We try to avoid fake pool with huge liquidity thanks to that check
            if float(pair["volumeUSD"]) > reserveUSD / 100:
                sum_ += reserveUSD
        last_id = str(queryExchange["data"]["pairs"][-1]["id"])
    return sum_


# Using API
def getPricesOf(tokenAddress):
    tokenAddress = tokenAddress.lower().replace(" ", "")
    try:
        tokenAddress = Web3.toChecksumAddress(Constants.symbol_to_address[tokenAddress])
    except:
        pass

    try:
        derivedPrice = getDerivedPriceOf(tokenAddress)
    except:
        return (
            "Error: Given address "
            + tokenAddress
            + " is not a valid Ethereum address or a valid symbol."
        )

    dPrice = int(derivedPrice) / E18
    avaxPrice = getAvaxPrice()
    return dPrice, (dPrice * avaxPrice)


def reloadAssets():
    last_id, queryExchange, tokens = "", {}, {}
    avaxPrice = getAvaxPrice()
    while last_id == "" or len(queryExchange["data"]["tokens"]) == 1000:
        queryExchange = genericQuery(
            '{tokens(first: 1000, where: {id_gt:"'
            + last_id
            + '"}){id, symbol, liquidity, derivedAVAX, volumeUSD}}'
        )
        for token in queryExchange["data"]["tokens"]:
            derivedLiq = float(token["liquidity"]) * float(token["derivedAVAX"])
            if (
                float(token["volumeUSD"]) >= derivedLiq * avaxPrice / 100
                and derivedLiq > 100
            ):
                tokens[token["id"]] = {
                    "symbol": token["symbol"].lower().strip(),
                    "liquidity": derivedLiq,
                }
        last_id = str(queryExchange["data"]["tokens"][-1]["id"])

    tokens = {
        k: v
        for k, v in reversed(
            sorted(tokens.items(), key=lambda item: item[1]["liquidity"])
        )
    }
    s2a = {}
    for address, token in tokens.items():
        if token["symbol"] not in s2a:
            s2a[token["symbol"]] = address
    Constants.symbol_to_address = s2a


def getAbout():
    joePrice = getJoePrice()
    avaxPrice = getAvaxPrice()
    csupply = float(getCirculatingSupply() / E18)
    mktcap = joePrice * csupply
    farm_tvl = getTraderJoeTVL()
    lending_tvl = float(getLendingTotalSupply() / E18)

    return (
        "$JOE: ${}\n"
        "$AVAX: ${}\n"
        "Market Cap: ${}\n"
        "Circ. Supply: {}\n"
        "Farm TVL: ${}\n"
        "Lending TVL: ${}\n"
        "Total TVL: ${}".format(
            readable(joePrice, 4),
            smartRounding(avaxPrice),
            smartRounding(mktcap),
            smartRounding(csupply),
            smartRounding(farm_tvl),
            smartRounding(lending_tvl),
            smartRounding(lending_tvl + farm_tvl),
        )
    )


def avg7d(timestamp):
    query = genericQuery(
        '{candles(where: {\
      token0: "0x6e84a6216ea6dacc71ee8e6b0a5b7322eebc0fdd",\
      token1: "0xc7198437980c041c805a1edcba50c1ce5db95118",\
      period: 14400,\
      time_lte: '
        + timestamp
        + "},orderBy: time,orderDirection: desc,first: 42) \
      {close, time}}",
        Constants.JOE_DEXCANDLES_SG_URL,
    )
    closes = query["data"]["candles"]
    logger.info(
        "\n".join(
            [
                "{}: {}".format(
                    round(1 / float(i["close"]), 2),
                    datetime.datetime.fromtimestamp(int(i["time"])),
                )
                for i in closes
            ]
        )
    )
    if len(closes) == 0:
        return -1
    return sum([1 / float(i["close"]) for i in closes]) / len(closes)


def getLendingAbout():
    lending_tvl = float(getLendingTotalSupply() / E18)
    totalBorrow = float(getLendingTotalBorrow() / E18)

    return (
        "Lending informations:\n"
        "Total Deposited: ${}\n"
        "Total Borrowed: ${}\n".format(
            smartRounding(lending_tvl), smartRounding(totalBorrow)
        )
    )


if __name__ == "__main__":
    # print(readable(getTraderJoeTVL()))
    # print(getLendingAbout())
    # print(getCurrentGasPrice() / 10**9)
    print(getMoneyMakerPositions(5_000, return_reserve_and_balance=True))
    # reloadAssets()
    # print(Constants.symbol_to_address)
    # print(addBuyBackLast7d(150))
    # print(len(getMoneyMakerPositions(10000)[0]))
    print("Done")
