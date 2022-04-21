import yfinance as yf
import os

def update_prices(symbol_list):
    prices = []
    for stock in symbol_list:
        msft = yf.Ticker(stock).history(period="1D")
        a=list(msft.to_dict().values())
        b = list(a[0])[0]
        price = (a[0])[b]
        prices.append(f'{round(price, 2)},')
    cur_file_path = os.path.dirname(os.path.abspath(__file__)).replace("\\","/")
    with open(f'{cur_file_path}/price.txt','w') as file:
        file.writelines(prices)
    print('UPDATED')

def price_list():
    stock_prices = []
    cur_file_path = os.path.dirname(os.path.abspath(__file__)).replace("\\","/")
    with open(f'{cur_file_path}/price.txt','r') as rfile:
        data = rfile.readlines()
        for line in data:
            stock_prices = line.split(',')
            return stock_prices