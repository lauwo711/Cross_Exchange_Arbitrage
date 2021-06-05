import hmac, hashlib, time, requests

API_KEY = ''
API_SECRET = ''

class Auth(requests.auth.AuthBase):
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key

    def __call__(self, request):
        nonce = str(int(1000 * time.time()))
        strBody = request.body.decode() if request.body else ''
        message = nonce + ':' + request.method + request.path_url + (strBody or '')
        signature = hmac.new(self.secret_key.encode(), message.encode(), hashlib.sha256).hexdigest()
        request.headers.update({
            'X-ACCESS-NONCE': nonce,
            'X-ACCESS-KEY': self.api_key,
            'X-ACCESS-SIGN': signature,
        })
        return request

my_auth = Auth(API_KEY, API_SECRET)

def aax_new_order(data):
    response = requests.post('https://api.aax.com/v2/spot/orders', json=data, auth=my_auth)
    return response
