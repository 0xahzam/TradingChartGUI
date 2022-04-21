import mysql.connector as con
import yfinance as yf
import pandas as pd
import mplfinance as mpf
import os
from pathlib import Path
from finding_stock import *
from statistics import *

from statistics import add_data

# passw : mySQL password
# sym : symbol of stock
# time_period : time frame of the stock

# plotting the data
def plot_graph(sym, dictt):
    def company_name(symbol):
        name = yf.Ticker(symbol).info['longName'].title()
        return name

    cur_file_path = os.path.dirname(os.path.abspath(__file__)).replace("\\","/")
    data = pd.read_csv(f'{cur_file_path}/{sym}.csv')
    sorted_data = data.sort_values(by=["Date"], ascending=True)
    sorted_data.to_csv(f'{cur_file_path}/{sym}.csv', index=False) #entering sorted data
    data = pd.read_csv(f'{cur_file_path}/{sym}.csv')
    data["Date"] = pd.to_datetime(data["Date"])
    data = data.set_index("Date")
    comp_name = company_name(sym)

    mpf.plot(
        data, type = dictt['plot_type'].lower(), figratio=(20, 10),
        ylabel="Price(USD)", title=f"{comp_name.title()}",
        mav=(20, 50, 100), style=dictt['plot_color'].lower(),
        volume = True if dictt['volume'] == 'True' else False
    )
    
    os.remove(f'{cur_file_path}/{sym}.csv')

# this function retrieves the financial data of a stock, stores it in mySQL (temporarily) then converts it into csv format
def stock(passw, sym, time_period):

    # converting the stock symbol name into a name which can be used as table name in SQL
    sym_sql = ""
    for i in sym:
        if i.isalnum():
            sym_sql += i

    # connecting the SQL database and creating a 'project database'
    mycon = con.connect(host="localhost", user="root", passwd=passw)
    cur = mycon.cursor()
    cur.execute('SHOW DATABASES LIKE "project"')
    result = cur.fetchone()
    if not result:
        cur.execute("CREATE DATABASE PROJECT")

    # creating the table which will contain all the financial data in the 'project database'
    mycon = con.connect(
        host="localhost",
        user="root",
        passwd=passw,
        database="project"
    )

    table_String = f"CREATE TABLE {sym_sql}(Date varchar(50),Open varchar(50), High varchar(50), Low varchar(50), Close varchar(50), Volume varchar(50))"
    cur = mycon.cursor()
    cur.execute(table_String)
    mycon.commit()

    # pulling the data financial from yahoo finance module (yfinance)
    symb = yf.Ticker(sym)
    a = symb.history(period=time_period)

    # converting the financial data from pandas dataframe into SQl and inserting in the stock table
    number_of_rows = len(a.index)
    i = 1
    cols = list(a.iloc[:, 1].to_dict().keys())
    col_list = list()
    for i in range(number_of_rows):
        col_list += [(str(cols[i]))]

    for i in range(number_of_rows):
        inp = (list(a.iloc[i].to_dict().values())[0:5])
        cur = mycon.cursor()
        input_string = "INSERT into {} values('{}','{}','{}','{}','{}','{}');".format(
            sym_sql, col_list[i-1], inp[0], inp[1], inp[2], inp[3], inp[4])
        cur.execute(input_string)
        mycon.commit()
        i += 1

    # All the financial data is stored in the SQL but for ploting purposes we need a csv file
    # Taking data from the SQL database and converting that into a csv file
    cur_file_path = os.path.dirname(os.path.abspath(__file__)).replace("\\","/")
    open_csv = open(f'{cur_file_path}/{sym_sql}.csv', 'w')
    query = f"SELECT * FROM {sym_sql}"
    cur.execute(query)
    while True:
        df = pd.DataFrame(cur.fetchmany(1000))
        if len(df) == 0:
            break
        else:
            headers = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
            df.to_csv(open_csv, header=headers)

    open_csv.close()
    cur.close()

    # Deleting the database project so that the code can be run again
    # also because the data is securely stored in the csv file

    mycon = con.connect(host="localhost", user="root", passwd=passw, database='project')
    cur = mycon.cursor()
    cur.execute(f"DROP TABLE {sym_sql}")

def onpress(passw, text_in, time_period, dictt):
    stock(passw, text_in, time_period)
    add_data(passw, text_in)
    plot_graph(text_in, dictt)