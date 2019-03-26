import time
import pybithumb
from datetime import datetime, timedelta

with open("bithumb.txt") as f:
    lines = f.readlines()
    # 좌우 공백을 제거한 문자열 저
    key = lines[0].strip()
    secret = lines[1].strip()
    bithumb = pybithumb.Bithumb(key, secret)


def get_target_price(ticker):
    df = pybithumb.get_ohlcv(ticker)
    # -1 today
    yesterday = df.iloc[-2]

    today_open = yesterday['close']
    yesterday_high = yesterday['high']
    yesterday_low = yesterday['low']
    #가격 변동폭 : 전일 고가 - 전일 저가
    #매수 기준 :당일 시간에서 (변동폭 * 0.5) 이상 상승하면 매수
    #매도 기준: 당일 종가에 매도
    target = today_open + (yesterday_high - yesterday_low) * 0.5
    return target


def buy_crypto_currency(ticker):
    # 잔고조회
    krw = bithumb.get_balance(ticker)[2]
    # 호가창 조회
    orderbook = pybithumb.get_orderbook(ticker)
    # 최우선 매도 호가 조회
    sell_price = orderbook['asks'][0]['price']
    # 원화잔고를 최우선 매도가로 나눠서 구매 가능한 수량 계산
    unit = krw / float(sell_price)
    # 시장가 주문으로 비트코인 매수
    bithumb.buy_market_order(ticker, unit)


def sell_cryto_currency(ticker):
    unit = bithumb.get_balance(ticker)[0]
    bithumb.sell_makret_order(ticker,unit)


now = datetime.now()
# timedelta는 1일 더하여 다음날 자정으로 만듬
mid = datetime(now.year, now.month, now.day) + timedelta(1)
target_price = get_target_price("BTC")

while True:
    try:
        now = datetime.now()
        if mid < now < mid + datetime.delta(seconds=10):
            target_price = get_target_price("BTC")
            mid = datetime(now.year, now.month, now.day) + timedelta(1)
            # 다음날 시초가에 전량 매도
            sell_cryto_currency("BTC")

        current_price = pybithumb.get_current_price("BTC")
        print(current_price)

        #목표가 이상이면 매수
        current_price = pybithumb.get_current_price("BTC")
        if current_price > target_price:
            buy_crypto_currency("BTC")
    except:
        print("에러 발생")
    time.sleep(1)

