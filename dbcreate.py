    #!/usr/bin/env python
    # coding: utf-8

def generatedb():
    import sqlite3
    import pandas as pd


    #connecting to database file
    conn = sqlite3.connect('CompanyAccounts.db')
    c = conn.cursor()


    c.execute('''CREATE TABLE IF NOT EXISTS subsidiaryCompanies (
        company_id INTEGER PRIMARY KEY NOT NULL, 
        company_name TEXT
        ); ''')     #creating subsidiaryCompanies table


    df = pd.read_excel(r'PracticalTask-Accounts.xlsx') #import list of accounts locally
    df.to_sql(name='accountsListTemp',if_exists='replace',con=conn, index_label='account_id') #setup in temp table


    c.executescript('''
      
        BEGIN TRANSACTION;
        DROP TABLE IF EXISTS accountsList;
        CREATE TABLE IF NOT EXISTS accountsList (account_list_id INTEGER PRIMARY KEY NOT NULL,
                                    account_list_account_code TEXT,
                                    account_list_account_name TEXT);
        
        INSERT INTO accountsList SELECT * FROM accountsListTemp;
        
        DROP TABLE accountsListTemp;
        COMMIT TRANSACTION;
        ''')

    conn.commit()

    #This is to create a table with a primary key - the df to sql function does not have this functionality.

    c.executescript('''
        BEGIN TRANSACTION;
        CREATE TABLE IF NOT EXISTS accountSelection (
                account_selection_id INTEGER PRIMARY KEY NOT NULL,
                account_list_id INTEGER NOT NULL,
                company_id INTEGER NOT NULL, 
                FOREIGN KEY (account_list_id) REFERENCES accountsList (account_list_id),
                FOREIGN KEY (company_id) REFERENCES subsidiaryCompanies (company_id));
        
        COMMIT TRANSACTION;''')
    conn.close()

    return

