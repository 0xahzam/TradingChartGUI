import mysql.connector as con

def check_for_table(passw):
    mycon = con.connect(host="localhost", user="root", passwd=passw, database="project")
    cur = mycon.cursor()
    cur.execute("SHOW TABLES LIKE 'stats'")
    result = cur.fetchone()
    if not result:
        cur.execute('CREATE TABLE stats (COMPANY_NAME varchar(50), TIMES_USED int)')

def check_for_db(passw):
    mycon = con.connect(host="localhost", user="root", passwd=passw)
    cur = mycon.cursor()
    cur.execute('SHOW DATABASES LIKE "project"')
    result = cur.fetchone()
    if not result:
        cur.execute("CREATE DATABASE PROJECT")

def check_for_company(company_name, passw):
    mycon = con.connect(host="localhost", user="root", passwd=passw, database='project')
    cur = mycon.cursor()
    cur.execute('SELECT company_name from stats')
    companies = cur.fetchall()
    presence = False
    for tuplee in companies:
        if company_name in tuplee:
            presence = True
    return presence

def add_data(passw, company_name):
    check_for_db(passw)
    check_for_table(passw)
    mycon = con.connect(host="localhost", user="root", passwd=passw, database='project')
    cur = mycon.cursor()
    in_table = check_for_company(company_name, passw)
    if in_table == True:
        cur.execute(f'UPDATE stats SET times_used = (times_used + 1) WHERE company_name = "{company_name}"')
        print('Updated')
    else:
        cur.execute(f"INSERT INTO stats (COMPANY_NAME, TIMES_USED) VALUES ('{company_name}',1)")
        print('Added')
    cur.execute('COMMIT')
