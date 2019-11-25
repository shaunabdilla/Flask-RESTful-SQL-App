from flask import (
    Flask,
    render_template,
    request,
    redirect,
    flash,
    url_for
)

import traceback
import sys
import sqlite3
import re
import random


# Create the application instance
app = Flask(__name__, template_folder="templates")
app.secret_key = "secret key"

# Import DB Creation Script
import dbcreate

# Create a URL route in our application for "/"
@app.route('/')
def home():
    """
    This function just responds to the browser ULR
    localhost:5000/

    :return:        the rendered template 'home.html'
    """
    dbcreate.generatedb()
    return render_template('home.html')

@app.route('/addrec',methods =['POST', 'GET']) #Posts information to Company Table
def addrec():
    cursor = sqlite3.connect('CompanyAccounts.db')
    # cursor.row_factory = lambda cursor, row: row[0]
    cur = cursor.execute("SELECT account_list_id, account_list_account_name FROM accountsList")
    result = cur.fetchall()
    print(result)
    print(type(result))

    if request.method == 'POST':
        try:
            companyname = request.form['companyname']
            multiselect = request.form.getlist('accountsel')
            print(multiselect)
            print(100*"-")

            with sqlite3.connect('CompanyAccounts.db') as conn:
                cur = conn.cursor()
                cur.execute(f"SELECT COUNT(*) from subsidiaryCompanies WHERE company_name='{companyname}'")
                existentname=str(returnnum(cur.fetchone()))
                print(existentname)
                if existentname == '0':
                    cur.execute("INSERT INTO 'subsidiaryCompanies' (company_name) VALUES (?)", (companyname,))
                    flash('Company created')
                else:
                    flash('Company already exists')
                    return render_template("home.html", companyname = companyname)
                    conn.commit
            cur = cursor.execute(f"SELECT company_id FROM subsidiaryCompanies WHERE company_name='{companyname}'")
            result = cur.fetchall()
            print(result)
            print(100*"*")
            for account in multiselect:
                print(account)
                print(returnnum(result))
                with sqlite3.connect('CompanyAccounts.db') as conn:
                    cur = conn.cursor()
                    cur.execute("INSERT INTO accountSelection (company_id, account_list_id) VALUES (?, ?)", (str(returnnum(result)), str(account)))
                    conn.commit
                
        except Exception as e:
            print('Unable to store record.', e)
            print("Exception in user code:")
            print("-"*60)
            traceback.print_exc(file=sys.stdout)
            print("-"*60)
            print('Record not added')
            conn.rollback()
            msg = 'Error in Insert Operation'
            return render_template('error.html', msg = msg)

        finally:
            with sqlite3.connect('CompanyAccounts.db') as conn:
                return render_template("home.html", companyname = companyname)
                conn.close()

    return render_template('company.html', accounts=result)


@app.route('/showrec', methods =['POST', 'GET']) #Shows Company Accounts Table
def showrec():
    if request.method == 'POST':
        try:
            companyname = request.form['companyname']
            # Connect to db
            cursor = sqlite3.connect('CompanyAccounts.db')
            print(companyname)
            cur = cursor.execute(f"SELECT company_id, company_name FROM subsidiaryCompanies WHERE company_name='{companyname}'")
            companyname = cur.fetchone()
            print(companyname[0])
            cur = cursor.execute(f"SELECT account_list_id, company_id FROM accountSelection WHERE company_id='{companyname[0]}'")
            result = cur.fetchall()
            print(result)
            accountidlist = tuple(extract(result)) # get the list of accounts from the list for that company
            print(accountidlist)
            cur = cursor.execute("SELECT account_list_id, account_list_account_name FROM accountsList WHERE account_list_id IN {}".format(accountidlist))
            rows = cur.fetchall()
            print(rows)
            return render_template('result.html', items = rows, companyname = companyname[1])

        except Exception as e:
            print('Unable to show record.', e)
            print("Exception in user code:")
            print("-"*60)
            traceback.print_exc(file=sys.stdout)
            print("-"*60)
            print('Record not found')
            msg = 'Error in Show Operation, Company probably does not exist in Database'
            return render_template('error.html', msg=msg)

    else:
        return render_template('display_company.html')

@app.route('/deleterec', methods =['POST', 'GET']) #Deletes Company from Table
def deleterec():
    if request.method == 'POST':
        try:
            companyname = request.form['companyname']
            # Connect to db
            cursor = sqlite3.connect('CompanyAccounts.db')
            print(companyname)
            cur = cursor.execute(f"SELECT company_id, company_name FROM subsidiaryCompanies WHERE company_name='{companyname}'")
            companyid_name = cur.fetchone()
            print(companyid_name)
            cur = cursor.execute(f"DELETE FROM accountSelection WHERE company_id={int(companyid_name[0])}")
            cur = cursor.execute(f"DELETE FROM subsidiaryCompanies WHERE company_name='{companyname}'")
            cursor.commit()
            flash('Company deleted')
            return redirect(url_for('home'))

        except Exception as e:
            print('Unable to show record.', e)
            print("Exception in user code:")
            print("-"*60)
            traceback.print_exc(file=sys.stdout)
            print("-"*60)
            print('Record not found')
            msg = 'Error in Show Operation, Company probably does not exist in Database'
            return render_template('error.html', msg=msg)

    else:
        return render_template('delete_company.html')

@app.route('/editrec', methods =['POST', 'GET'])
def editrec():
    if request.method == 'POST' and request.form['notempty'] == "":
            companyname = request.form['companyname']
            multiselect = request.form.getlist('accountsel')
            cursor = sqlite3.connect('CompanyAccounts.db')
            cur = cursor.execute(f"SELECT company_id FROM subsidiaryCompanies WHERE company_name='{companyname}'")
            result = cur.fetchall()
            print(int(returnnum(result)))
            cursor.execute(f"DELETE FROM accountSelection WHERE company_id={int(returnnum(result))}")
            cursor.commit()
            for account in multiselect:
                print(account)
                print(returnnum(result))
                cur = cursor.execute("INSERT INTO accountSelection (company_id, account_list_id) VALUES (?, ?)", (str(returnnum(result)), str(account)))
                cursor.commit()
            flash('Company accounts updated')
            return redirect(url_for('home'))

    elif request.method == 'POST':
        try:
            companyname = request.form['companyname']
            # Connect to db
            cursor = sqlite3.connect('CompanyAccounts.db')
            cur = cursor.execute("SELECT account_list_id, account_list_account_name FROM accountsList")
            result = cur.fetchall() # Getting list of all the accounts available in the sheet
            print(companyname)
            print("-"*60)
            cur = cursor.execute(f"SELECT company_id, company_name FROM subsidiaryCompanies WHERE company_name='{companyname}'")
            companyid_name = cur.fetchone() # Getting the companyid from the companies table
            print(companyid_name)
            print("-"*60)
            cur = cursor.execute(f"SELECT account_list_id FROM accountSelection WHERE company_id={int(companyid_name[0])}")
            listid = cur.fetchall() #Getting the list of selected accounts ids
            print(listid)
            print("-"*60)
            tuplelistid = tuple(extract(listid))
            print(tuplelistid)
            print("-"*60)
            cur = cursor.execute("SELECT account_list_id, account_list_account_name FROM accountsList WHERE account_list_id IN {}".format(tuplelistid))
            rows = cur.fetchall() #Getting the list of selected accounts names
            print("-"*60)
            print(rows)
            print("-"*60)
            print(companyid_name)
            print("-"*60)
            return render_template('accounts_edit.html', accounts_sel = rows, companyid_name = companyid_name, accounts = result, selection = tuplelistid )

        except Exception as e:
            print('Unable to show record.', e)
            print("Exception in user code:")
            print("-"*60)
            traceback.print_exc(file=sys.stdout)
            print("-"*60)
            print('Record not found')
            msg = 'Error in Show Operation, Company probably does not exist in Database'
            return render_template('error.html', msg=msg)

    else:
        return render_template('edit_company.html')


@app.route('/error')
def error():

    return render_template('error.html')

def returnnum(clean): #using regexp to clean result before input into db
    return re.sub('[^0-9]','', str(clean))

def extract(lst): #returning the first item of a list
    return [item[0] for item in lst]
# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    app.run(debug=True)