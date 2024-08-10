import json
import logging

import requests

from joeBot import Constants


logger = logging.getLogger(__name__)


def query(pair_address, query=None):
    r = requests.get(
        f"{Constants.BARN_URL}{pair_address.lower()}",
        json=query,
        headers={"x-traderjoe-api-key": Constants.BARN_KEY},
    )
    assert r.status_code == 200
    return json.loads(r.text)


def get_joe_price():
    lb_joe_avax_25bp = query(Constants.LB_JOE_AVAX_25BP)

    price_usd = float(lb_joe_avax_25bp["tokenX"]["priceUsd"])
    price_native = float(lb_joe_avax_25bp["tokenX"]["priceNative"])

    return (price_usd, price_native)


def get_avax_price():
    lb_avax_usdc_20bp = query(Constants.LB_AVAX_USDC_20BP)
    return (float(lb_avax_usdc_20bp["tokenX"]["priceUsd"]), 1.0)


if __name__ == "__main__":
    print(get_joe_price())
    print(get_avax_price())
