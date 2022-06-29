import os
from turtle import pu
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
puid = "";

access_key = "aaaaaaaaaaaacSY4BIf8fRW9WbpACAa03bS95qZg";
secret_key = "aaaaaaaaaaaal09kDGy6FUmoBstHXS7WaGuwx0T5";
server_url = "https://api.upbit.com";

project_url = "https://console.firebase.google.com/project/tuning-9b90e/firestore/";
cred = credentials.Certificate("/home/ubuntu/tuning-9b90e-firebase-adminsdk-cakmk-1015e5df95.json")
firebase_admin.initialize_app(cred, {
  'projectId': 'tuning-9b90e',
})

# @app1.route('/get', methods = ['GET', 'POST'])
# def a():
#     return jsonify({
#     'uid' : puid,
#     'currencies' : currencies,
#     'amount' : strs})

@app1.route('/read', methods=['POST'])
def c():
    global access_key, secret_key, puid
    request_data = request.data
    request_data = json.loads(request_data.decode('utf-8'))
    access_key = request_data['accessKey']
    secret_key = request_data['secretKey']
    puid = request_data['uid']
    #return access_key + secret_key + puid

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
    