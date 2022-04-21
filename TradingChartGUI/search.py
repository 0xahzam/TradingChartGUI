from logging import exception
from current_price import *

symbol_list = [
    "AAPL","TSLA","ADBE","GOOGL","AMZN","SONY","SPOT","MSFT","FB","KO","SNAP","GME",
    "MRNA","NFLX","QCOM","SQ","COIN","INFY","BA","ZM"
]

company_name_list = [
    "Apple Inc.","Tesla Inc.","Adobe Inc.", "Alphabet Inc.","Amazon, Inc.",
    "Sony Group Corporation","Spotify Technology S.A.","Microsoft Corporation","Facebook,Inc.",
    "The Coca-Cola Company","Snap Inc.","Gamestop Corporation","Moderna, Inc.","Netflix, Inc.","Qualcomm Incorporated",
    "Square, Inc.","Coinbase Global, Inc.","Infosys Ltd","Boeing Company (The)","Zoom video communications, Inc."
]
num = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]

def type_col(text):
    stock_prices = price_list()
    if text in company_name_list:
        place = 'company_list_name'
        pos = company_name_list.index(text)
    elif text.upper() in symbol_list:
        place = 'symbol_list'
        pos = symbol_list.index(text)
    elif text[0] == '$':
        if text[1::] in stock_prices :
            place = 'price_list'
            pos = stock_prices.index(text[1::])
    elif text[0] != '$':
        if int(text) in num:
            place  = 'num'
            pos = num.index(int(text))
    return place, pos

#place, pos = type_col('3')
#print(place,pos)