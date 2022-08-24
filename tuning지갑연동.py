from time import sleep
import pyupbit

import json

from flask import Flask, jsonify
from flask import request

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import db

app1 = Flask(__name__)
strs = []
currencies = []

#튜닝에 필요한 변수들
percents = [60, 10, 10, 20]
crc_krw = [40000, 20000, 10000, 30000]
p_length = 4

havingmoney = 100000.0
depth = 0.15

server_url = "https://api.upbit.com";

project_url = "https://console.firebase.google.com/project/tuning-9b90e/firestore/";
cred = credentials.Certificate("/home/ubuntu/tuning-9b90e-firebase-adminsdk-cakmk-1015e5df95.json")
firebase_admin.initialize_app(cred, {
  'projectId': 'tuning-9b90e',
})


@app1.route('/read', methods=['POST', 'GET'])
def c():
    global access_key, secret_key, puid, upbit, balances
    if(request.method == 'POST') :
        request_data = request.data
        request_data = json.loads(request_data.decode('utf-8'))
        access_key = request_data['accessKey']
        secret_key = request_data['secretKey']
        puid = request_data['uid']
        upbit = pyupbit.Upbit(access_key, secret_key)
        balances = upbit.get_balances()
    return "";

@app1.route('/add', methods = ['GET'])
def b():    
    get_currencies()
    db = firestore.client()

    doc_ref = db.collection(u'cryptoData').document(u'tuning'+puid)
    doc_ref.set({
        u'currencies' : currencies,
        u'amount' : strs,
        u'uid': puid
    })
    return "";

def get_currencies():  
    global currencies, strs
    currencies = []
    strs = []
    for i in balances:
        amount = 0;
        amount = upbit.get_amount(i['currency']);
        if(amount > 0):
            currencies.append(i['currency'])
            strs.append(amount)

@app1.route('/tuning', methods=['POST', 'GET'])
def c():
    global upbit, balances, percents, p_length
    if(request.method == 'POST') :
        request_data = request.data
        request_data = json.loads(request_data.decode('utf-8'))
        percents = request_data['percents']
        p_length = request_data['p_length']
    return "";

def get_balance(ticker):
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return int(b['balance'])
            else:
                return 0
    return 0

def buy_market(ticker, price):
    upbit.buy_market_order(ticker=ticker, price=price*0.9995)

def sell_market(ticker, price):
    upbit.sell_market_order(ticker=ticker, price=price*0.9995)

def tuning():
    global buy_amount, upbit
    buy_amount = [0, 0, 0, 0]
    while(1):
        for i in range(p_length):
            buy_amount[i] = havingmoney * percents[i] / 100.0
            print('having money : %0.0f' %crc_krw[i])
            if crc_krw[i] > (buy_amount[i] + (buy_amount[i] * depth)) :
                buyt = crc_krw[i] - buy_amount[i]
                print('SELL : %0.0f' %buyt)
                sumc = crc_krw[i] - buyt
                print('NOW : %0.0f' %sumc)
            elif crc_krw[i] < (buy_amount[i] - (buy_amount[i] * depth)):
                buyt = buy_amount[i] - crc_krw[i]
                print('BUY : %0.0f' %buyt)
                sumc = crc_krw[i] + buyt
                print('NOW : %0.0f' %sumc)

                #총매수금액
                print(upbit.get_amount('ALL'))
        # sleep(10)
        break;
    return 0;

if __name__ == '__main__':
    app1.run(host='0.0.0.0', port=5000, debug=True)