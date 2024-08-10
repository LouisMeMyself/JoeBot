# import numpy as np
# import plotly.graph_objects as go

# from joeBot import Constants, JoeSubGraph
# from joeBot.JoeSubGraph import getTokenCandles


# def getTokenCandlesPerAvax(token_address, period, nb):
#     token_candle = getTokenCandles(token_address, period, nb)
#     if token_address == Constants.WAVAX_ADDRESS:
#         return token_candle[::-1]

#     avax_candle = getTokenCandles(Constants.WAVAX_ADDRESS, period, nb)

#     avax_candle = avax_candle[: len(token_candle)]
#     token_candle = token_candle[: len(avax_candle)]

#     data_df = token_candle.mul(avax_candle)
#     data_df = data_df.iloc[::-1]

#     return data_df


# def getChart(token_symbol, period):
#     token_symbol = token_symbol.lower().replace(" ", "")
#     try:
#         try:
#             if token_symbol == "avax":
#                 token_address = Constants.WAVAX_ADDRESS
#             else:
#                 token_address = Constants.symbol_to_address[token_symbol]
#         except:
#             token_address = JoeSubGraph.w3.toChecksumAddress(token_symbol)
#     except:
#         raise KeyError

#     if period == "month":
#         p, nb, t = "86400", "31", "days"
#     elif period == "day":
#         p, nb, t = "3600", "24", "hours"
#     else:
#         return

#     try:
#         candlesticks_pd = getTokenCandlesPerAvax(token_address, p, nb)
#         # Sometime low > high
#         candlesticks_pd["low"], candlesticks_pd["high"] = np.where(
#             candlesticks_pd["low"] > candlesticks_pd["high"],
#             [candlesticks_pd["high"], candlesticks_pd["low"]],
#             [candlesticks_pd["low"], candlesticks_pd["high"]],
#         )
#         # Exclude fake highs that ruins the chart
#         candlesticks_pd["high"] = np.where(
#             candlesticks_pd["high"]
#             > candlesticks_pd[["open", "close"]].values.max(1) * 10,
#             candlesticks_pd[["open", "close"]].values.max(1),
#             candlesticks_pd["high"],
#         )
#         # Exclude fake lows that ruins the chart
#         candlesticks_pd["low"] = np.where(
#             candlesticks_pd["low"]
#             < candlesticks_pd[["open", "close"]].values.min(1) / 10,
#             candlesticks_pd[["open", "close"]].values.min(1),
#             candlesticks_pd["low"],
#         )
#     except Exception as e:
#         raise e

#     try:
#         fig = go.Figure(
#             data=[
#                 go.Candlestick(
#                     x=candlesticks_pd.index,
#                     open=candlesticks_pd["open"],
#                     high=candlesticks_pd["high"],
#                     low=candlesticks_pd["low"],
#                     close=candlesticks_pd["close"],
#                 )
#             ],
#         )
#         fig.update_layout(
#             xaxis_rangeslider_visible=False,
#             title={
#                 "text": "Price of {} during the last {} {}".format(
#                     token_symbol.upper(), len(candlesticks_pd), t
#                 ),
#                 "font": {"size": 40},
#                 "x": 0.5,
#                 "xanchor": "center",
#             },
#             yaxis_title="Price in USD",
#             xaxis_title="UTC Date",
#         )
#         fig.write_image("content/images/chart.png", width=1400, height=1000, scale=2)
#     except Exception as e:
#         raise e


# if __name__ == "__main__":
#     JoeSubGraph.reloadAssets()
#     getChart("elk", "day")
