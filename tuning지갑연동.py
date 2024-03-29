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
coin_amount = []

#튜닝에 필요한 변수들
percents = [0, 0]
buyset = []
p_length = 0

buyset_sum = 0.0
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
        u'coin_amount' : coin_amount,
        u'uid': puid
    })
    return "";

def get_currencies():  
    global currencies, strs, coin_amount, cur_dict
    currencies = []
    strs = []
    coin_amount = []
    cur_dict = {}
    for i in balances:
        global temp, amount2
        amount = 0
        amount2 = 0
        temp = 0
        name = "KRW-"+i['currency']
        if i['currency'] != 'KRW' and i['currency'] != 'APENFT' and i['currency'] != 'XYM' and i['currency'] != 'ETHF' and i['currency'] != 'ETHW':
            # print(name)
            amount = pyupbit.get_current_price(name) * upbit.get_balance(i['currency'])
            # amount = upbit.get_amount(i['currency'])
            if(amount >= 1):
                currencies.append(i['currency'])
                strs.append(amount)
                cur_dict[i['currency']] = amount
                # 여기까지 작업했는데, 작업 내용은 딕셔너리에 키, 값으로 내림차순 정렬해서 [coinname, amount]로 넣어둔 상태이고
                # 이걸 이용해서 currencies를 딕셔너리의 키로 대체하고 strs를 딕셔너리의 값으로 대체해야한다. 
                coin_amount.append(upbit.get_balance(i['currency']))

@app1.route('/tuning', methods=['POST', 'GET'])
def start_tune():
    global upbit, balances, percents, p_length, depth
    if(request.method == 'POST') :
        request_data = request.data
        request_data = json.loads(request_data.decode('utf-8'))
        percents = request_data['percents']
        p_length = request_data['p_length']
        print(percents)
        print(p_length)
        depth = request_data['depth']
        get_currencies()
        tuning()
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
    upbit.buy_market_order("KRW-"+ticker, (price*0.9995)-1000)

def sell_market(ticker, price):
    volume = (price/pyupbit.get_current_price("KRW-"+ticker)*0.9995)
    print(pyupbit.get_current_price("KRW-"+ticker))
    print(volume)
    upbit.sell_market_order("KRW-"+ticker, volume)

def reserve():
    global buyarr, sumarr
    for i in range(barr_count):
        if buyarr[i] != None and sumarr[i] != None:
            print('%d , BUY : %0.0f' %(i, buyarr[i]))
            print('%d , NOW : %0.0f' %(i, sumarr[i]))
            #구매하기
            buy_market(currencies[i], buyarr[i])
        else:
            break

def tuning():
    global buy_amount, upbit, buyarr, sumarr, barr_count, percents, buyset_sum, values_list, key_list
    buy_amount = [0] * p_length
    buyarr = [0] * p_length
    sumarr = [0] * p_length
    barr_count = 0
    buyset_sum = 0
    # strs.sort(reverse=True)
    sorted(cur_dict.items(), key=lambda x: x[1], reverse=True)
    values_list = list(cur_dict.values())
    key_list = list(cur_dict.keys())
    print(cur_dict)
    for i in range(p_length):
        buyset_sum += values_list[i]
    while(3):
        for i in range(p_length):
            buy_amount[i] = buyset_sum * percents[i] / 100.0
            print('having money : %0.0f' %values_list[i])

            #코인 가치가 제한 폭 만큼 보다 더 클 때
            if values_list[i] > (buy_amount[i] + (buy_amount[i] * depth)) :
                for j in range(p_length):
                    buy_amount[j] = buyset_sum * percents[j] / 100.0
                    if values_list[j] > buy_amount[j] :
                        buyt = values_list[j] - buy_amount[j]
                        print('%d , SELL : %0.0f' %(j, buyt))
                        sumc = values_list[j] - buyt
                        print('%d , NOW : %0.0f' %(j, sumc))
                        sell_market(key_list[j], buyt)
                    elif values_list[j] < buy_amount[j]:
                        buyarr[barr_count] = buy_amount[j] - values_list[j]
                        # print('%d , BUY : %0.0f' %(j, buyt))
                        sumarr[barr_count] = values_list[j] + buyarr[barr_count]
                        # print('%d , NOW : %0.0f' %(j, sumc))
                    barr_count += 1
                break;

            #코인 가치가 제한 폭 만큼 보다 더 작을 때
            elif values_list[i] < (buy_amount[i] - (buy_amount[i] * depth)):
                for j in range(p_length):
                    buy_amount[j] = buyset_sum * percents[j] / 100.0
                    if values_list[j] > buy_amount[j] :
                        buyt = values_list[j] - buy_amount[j]
                        print('%d , SELL : %0.0f' %(j, buyt))
                        sumc = values_list[j] - buyt
                        print('%d , NOW : %0.0f' %(j, sumc))
                        sell_market(key_list[j], buyt)
                    elif values_list[j] < buy_amount[j]:
                        buyarr[barr_count] = buy_amount[j] - values_list[j]
                        # print('%d , BUY : %0.0f' %(j, buyt))
                        sumarr[barr_count] = values_list[j] + buyarr[barr_count]
                        # print('%d , NOW : %0.0f' %(j, sumc))
                break;
        reserve()
        break;
    return 0;

if __name__ == '__main__':
    app1.run(host='0.0.0.0', port=5000, debug=True)