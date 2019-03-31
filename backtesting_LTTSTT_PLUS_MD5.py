

#pip install openpyxl

import pybithumb
import numpy as np
import datetime

k = 0.5
init_balance = 10000000
bithumb_fee = 0.0015

def fee_calu(df) :
    # 슬리피지 제외
    # 수수료는 매수 체결 수량에 부과  / 매도 거래 금액에 부과
    cur_balance = init_balance
    time_limit = datetime.datetime(2013, 12, 28, 00, 00,00)

    for i in df.index :
        if i < time_limit:
            continue
        #print(i)
        # 매수체결가
        buy_price = df.ix[i,'target']

        # 매도체결가
        sell_price = df.ix[i,'close']

        if df.ix[i, 'high'] > buy_price and df.ix[i, 'bull'] :

            # 매수체결수량
            num_of_buy_no_fee = cur_balance / buy_price
            # 매수체결수량 (수수료 제외)
            num_of_buy = num_of_buy_no_fee - (num_of_buy_no_fee * bithumb_fee)
            # 매도체결수량 (매수체결수량 전량 매도)
            num_of_sell = num_of_buy
            # 거래금액
            tot_price_no_fee = num_of_sell * sell_price
            # 거래금액(수수료제외)
            tot_price = tot_price_no_fee - (tot_price_no_fee * bithumb_fee)

            #현재 보유 금액
            df.ix[i,'balance'] = tot_price
            # 실제 수익률(배)
            ror = (tot_price / num_of_sell) / (cur_balance / num_of_buy)
            df.ix[i, 'ror'] = ror

            cur_balance = tot_price
        else:
            df.ix[i, 'balance'] = cur_balance
            df.ix[i, 'ror'] = 1



df = pybithumb.get_ohlcv("BTC")
#df.to_excel("ETH_d.xlsx")


# 5일 이동 평균
df['ma5'] = df['close'].rolling(window=5).mean().shift(1)
#모든 row에 대해서 range 계산
df['range'] = (df['high'] - df['low']) * k
df['target'] = df['open'] + df['range'].shift(1)
df['bull'] = df['open'] > df['ma5']


#거래수수료
#TODO 수수료 계산 부분 구현
fixed_fee = 0.0032


'''
    매수 : 고가 > 목표가 일대, 
    매도 : 종가에 매도 
    매수 조건이 만족되지 않으면, 수익률 1 
'''

# 수익률 게산
df['org_ror'] = np.where( (df['high'] > df['target']) & df['bull'],
                      df['close'] / df['target']-fixed_fee , 1)

#기간 수익률 계산
df['org_hpr'] = df['org_ror'].cumprod()

#낙폭 계산 (drawdown)
df['org_dd'] = (df['org_hpr'].cummax() - df['org_hpr'])  / df['org_hpr'].cummax() * 100

#
fee_calu(df)

#기간 수익률 계산
df['hpr'] = df['ror'].cumprod()

#낙폭 계산 (drawdown)
df['dd'] = (df['hpr'].cummax() - df['hpr'])  / df['hpr'].cummax() * 100

#최대 낙폭 계산
print('MDD: ', df['dd'].max())
print('HPR: ', df['hpr'][-2])
df.to_excel('larry_ma2.xlsx')


'''
def fee_calu (df) :
    buy_price = df['target']
    # 매도체결가
    sell_price = df['close']
    # 매수체결수량
    num_of_buy_no_fee = cash / buy_price
    # 매수체결수량 (수수료 제외)
    num_of_buy = num_of_buy_no_fee - (num_of_buy_no_fee * bithumb_fee)
    # 매도체결수량 (매수체결수량 전량 매도)
    num_of_sell = num_of_buy
    # 거래금액
    tot_price_no_fee = num_of_sell * sell_price
    # 거래금액(수수료제외)
    tot_price = tot_price_no_fee - (tot_price_no_fee * bithumb_fee)

    # 실제 수익률(배)
    ror = (tot_price / num_of_sell) / (cash / num_of_buy)

    df['ror'] = np.where((df['high'] > df['target']) & df['bull'],
                         ror, 1)
'''