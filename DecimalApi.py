from RequestsRetry import requests_retry_session


class DecimalApi:
    def __init__(self, config):
        self.main_coin = config['decimal']['main_coin']
        self.api_url = config['decimal']['api_url']

    def actual_block(self):
        url = self.api_url + '/block/height'
        return int(requests_retry_session().get(url).json()) - 5

    def block_txs(self, height):
        url = self.api_url + '/block/{}/txs'.format(height)
        response = requests_retry_session().get(url).json()
        return response['result']

    def coin(self, symbol):
        url = self.api_url + '/coin/{}'.format(symbol)
        response = requests_retry_session().get(url).json()
        return response['result']

    def balance(self, address):
        url = self.api_url + '/address/{}'.format(address)
        response = requests_retry_session().get(url).json()
        pretty_balance = int(round(float(response['result']['balance'][self.main_coin]) * 0.000000000000000001, 3))
        return str(pretty_balance) + ' ' + self.main_coin.upper()

    @staticmethod
    def nft_token(uri):
        response = requests_retry_session().get(uri).json()
        return response['result']['token']

    @staticmethod
    def reserve_to_title(value):
        value = int(float(value))
        if value >= 1000:
            return str(int(value / 1000)) + 'K'
        return value
