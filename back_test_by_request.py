import requests
import json
import os
import logging
import time
import traceback
from datetime import datetime

today    = datetime.now()
log_file = os.path.dirname(__file__) + r"/log/" + os.path.basename(__file__).replace('.py','') + '_' + today.strftime("%Y%m%d%H%M%S") + ".log"
logger   = logging.getLogger(__name__)
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s.%(msecs)03d %(name)-12s %(levelname)-8s %(message)s')

# base = USDT
pair='BCHUSDT'
bn_fee = 0.001 #0.1%
re_fee = 0.001 #0.1%
bn_base_bal=500
bn_quo_bal =10
re_base_bal=500
re_quo_bal =10
pnl        =0
qty        =0.02
threshold  =round((1-bn_fee)*(1-re_fee),2)

while True:
    try:
        bn_url  = requests.get('https://api.binance.com/api/v3/depth?symbol='+pair+'&limit=5')
        re_url  = requests.get('https://api.aax.com/v2/market/orderbook?symbol='+pair+'&level=20')

        bn_resp = bn_url.json()
        bn_best_bid = bn_resp['bids'][0]
        bn_best_ask = bn_resp['asks'][0]

        re_resp = re_url.json()
        re_best_bid = re_resp['bids'][0]
        re_best_ask = re_resp['asks'][0]

        px_re   = round((float(re_best_bid[0]) + float(re_best_ask[0]))*0.5,2)
        px_bn   = round((float(bn_best_bid[0]) + float(bn_best_ask[0]))*0.5,2)
        pnl_trd = 0
        
        if threshold > px_bn/px_re: #px_re > px_bn:
            
            #craete binance buy order
            #create aax sell order

            bn_quo_bal  += qty*(1-bn_fee)
            bn_base_bal -= px_bn*qty
            re_quo_bal  -= qty*(1-bn_fee)
            re_base_bal += px_re*qty*threshold
            pnl_trd = px_re*qty*threshold - px_bn*qty
            
            pnl += pnl_trd
            logger.info("%s %s %s %s %s %s",pnl_trd, pnl, bn_base_bal, bn_quo_bal, re_base_bal, re_quo_bal)
                
        elif threshold > px_re/px_bn: #px_re < px_bn:
            
            #craete binance sell order
            #create aax buy order
            
            re_quo_bal  += qty*(1-re_fee)
            re_base_bal -= px_re*qty
            bn_quo_bal  -= qty*(1-re_fee)
            bn_base_bal += px_bn*qty*threshold
            pnl_trd = px_bn*qty*threshold - px_re*qty
            
            pnl += pnl_trd
            logger.info("%s %s %s %s %s %s",pnl_trd, pnl, bn_base_bal, bn_quo_bal, re_base_bal, re_quo_bal)
                
        print(pnl_trd, px_bn, px_re)
    except:
        traceback.print_exc()
        time.sleep(5)
        continue

