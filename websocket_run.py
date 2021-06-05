import requests
import json
import os
import logging
import time
import traceback
import threading
import websocket
from datetime import datetime
from Util_BN  import bn_new_order
from Util_AAX import aax_new_order

today    = datetime.now()
log_file = os.path.dirname(__file__) + r"/log/" + os.path.basename(__file__).replace('.py','') + '_' + today.strftime("%Y%m%d%H%M%S") + ".log"
logger   = logging.getLogger(__name__)
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s.%(msecs)03d %(name)-12s %(levelname)-8s %(message)s')
logger.info("pnl_trd, pnl, bn_base_bal, bn_quo_bal, re_base_bal, re_quo_bal, px_bn, px_re")

# base currency = USDT
pair='THETAUSDT'
bn_fee = 0.001 #0.1%
re_fee = 0.001 #0.1%
bn_base_bal=300
bn_quo_bal =50
re_base_bal=300
re_quo_bal =50
pnl        =0
qty        =1.6
rnd        =8
threshold  =round((1-bn_fee)*(1-re_fee),6)
logger.info("%s %s %s %s %s %s %s %s",pnl_trd, pnl, bn_base_bal, bn_quo_bal, re_base_bal, re_quo_bal, px_bn, px_re)

#fetch order book data from web socket of another exchange
def ws_re():
    global ws_re
    global re_ws_resp
    ws_re = websocket.WebSocket()
    ws_re.connect("wss://realtime.aax.com/marketdata/v2/")
    ws_re.send('{"e": "subscribe", "stream": "' + pair + '@book_20"}')
    
    try:
        while True:
            re_ws_resp = ws_re.recv()
            #print('RE')
            #print(re_ws_resp)
    except websocket._exceptions.WebSocketConnectionClosedException:
        print('socket connection closed')

#fetch data from web socket of Binance
def ws_bn():
    global ws_bn
    global bn_ws_resp
    ws_bn = websocket.WebSocket()
    ws_bn.connect("wss://stream.binance.com:9443/ws")
    ws_bn.send('{"method": "SUBSCRIBE","params":["' + pair.lower() + '@bookTicker"],"id": 1}')

    try:
        while True:
            bn_ws_resp = ws_bn.recv()
            #print('BN')
            #print(bn_ws_resp)
    except websocket._exceptions.WebSocketConnectionClosedException:
        print('socket connection closed')

def cross_ex_arbitrage():
    global bn_quo_bal
    global bn_base_bal
    global re_quo_bal
    global re_base_bal
    global qty
    global threshold
    global rnd
    global pnl
    global bn_fee
    global re_fee
    
    threading.Timer(0.1, cross_ex_arbitrage).start() # run every 0.1sec
    while True:
        try:
            re_best_ask=json.loads(re_ws_resp)['asks'][0][0]
            re_best_bid=json.loads(re_ws_resp)['bids'][0][0]

            bn_best_ask=json.loads(bn_ws_resp)['a']
            bn_best_bid=json.loads(bn_ws_resp)['b']

            px_re   = round((float(re_best_bid) + float(re_best_ask))*0.5,rnd)
            px_bn   = round((float(bn_best_bid) + float(bn_best_ask))*0.5,rnd)

            pnl_trd = 0

            if threshold > px_bn/px_re: #px_re > px_bn:

                #craete buy order at biance
                #create sell order at another exchange

                #record
                bn_quo_bal  += qty*(1-bn_fee)
                bn_base_bal -= px_bn*qty
                re_quo_bal  -= qty*(1-bn_fee)
                re_base_bal += px_re*qty*threshold
                pnl_trd      = px_re*qty*threshold - px_bn*qty

                pnl += pnl_trd
                logger.info("%s %s %s %s %s %s %s %s",pnl_trd, pnl, bn_base_bal, bn_quo_bal, re_base_bal, re_quo_bal, px_bn, px_re)

            elif threshold > px_re/px_bn: #px_re < px_bn:

                #craete sell order at biance
                #create buy order at another exchange

                re_quo_bal  += qty*(1-re_fee)
                re_base_bal -= px_re*qty
                bn_quo_bal  -= qty*(1-re_fee)
                bn_base_bal += px_bn*qty*threshold
                pnl_trd      = px_bn*qty*threshold - px_re*qty

                pnl += pnl_trd
                logger.info("%s %s %s %s %s %s %s %s",pnl_trd, pnl, bn_base_bal, bn_quo_bal, re_base_bal, re_quo_bal, px_bn, px_re)

            print(pnl_trd, px_bn, px_re)

        except:
            traceback.print_exc()
        
if __name__ == "__main__":
    try:
        t1 = threading.Thread(target=ws_re)
        t2 = threading.Thread(target=ws_bn)
        t1.start()
        t2.start()
        cross_ex_arbitrage()
    except:
        traceback.print_exc()
