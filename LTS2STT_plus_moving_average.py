import time
import pybithumb
from datetime import datetime, timedelta

# 키 유출 방지를 위해, 매수/매도를 위한 공개키/암호키를 파일로 저장 후 불러옴
with open("bithumb.txt") as f:
    lines = f.readlines()
    # 좌우 공백을 제거한 문자열 제거
    key = lines[0].strip()
    secret = lines[1].strip()
    bithumb = pybithumb.Bithumb(key, secret)

# 전일 5일 이동평균
def get_yesterday_ma5(ticker):
    df = pybithumb.get_ohlcv(ticker)
    close = df['close']
    ma = close.rolling(window=5).mean()
    return ma[-2]

# 목표 가격을 얻어옴
def get_target_price(ticker):
    #일봉 데이터 얻어옴
    df = pybithumb.get_ohlcv(ticker)
    #뒤에서 부터 마지막 일봉값. 예) df.iloc[-1] 는 today
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
    #시장가 주문으로 비트코인 매도
    bithumb.sell_makret_order(ticker,unit)


now = datetime.now()
# timedelta는 1일 더하여 다음날 자정으로 만듬
mid = datetime(now.year, now.month, now.day) + timedelta(1)

#비트코인의 목표 매수 가격
target_price = get_target_price("BTC")

while True:
    try:
        now = datetime.now()
        # 10초 마진으로 자정이 되면 전량 매도
        if mid < now < mid + datetime.delta(seconds=10):
            target_price = get_target_price("BTC")
            mid = datetime(now.year, now.month, now.day) + timedelta(1)
            # 다음날 시초가에 전량 매도
            sell_cryto_currency("BTC")

        #비트코인의 현재 가격
        current_price = pybithumb.get_current_price("BTC")
        print(current_price)

        # 목표가 이상이면서 상승장일 때 매수 ( 전일 5일의 이동평균값보다 클 때)
        if current_price > target_price and (current_price > ma5):
            buy_crypto_currency("BTC")
    except:
        print("에러 발생")
    time.sleep(1)
