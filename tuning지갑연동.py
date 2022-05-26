
import os
import pyupbit

from flask import Flask, jsonify
from flask import request

app1 = Flask(__name__)
strs = []
currencies = []

access_key = "User access key";
secret_key = "User access key";
server_url = "https://api.upbit.com";

@app1.route('/', methods = ['GET', 'POST'])
def index():
    strs = []
    currencies = []
    get_currencies()
    return jsonify({ 'currencies' : currencies,
    'amount' : strs})

@app1.route('/read', methods=['POST'])
def inde():
    access_key = request.form['accessKey']
    secret_key = request.form['secretKey']
    print(access_key + secret_key)
    return access_key + secret_key



upbit = pyupbit.Upbit(access_key, secret_key)

balances = upbit.get_balances()


def get_currencies():  
    for i in balances:
        amount = upbit.get_amount(i['currency']);
        if(amount > 0):
            currencies.append(i['currency'])
            strs.append(amount)

def get_currency_amount(cname):  
    am = 0;
    for i in balances:
        if(i['currency'] == cname):
            upbit.get_amount(i['currency']);
    return am;



if __name__ == '__main__':
    app1.run(host='0.0.0.0', port=5000, debug=True)