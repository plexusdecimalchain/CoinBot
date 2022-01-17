import logging
import configparser

import requests

from DecimalApi import DecimalApi
from TelegramApi import TelegramApi
import LatestParsedBlock as latestBlock
from time import sleep


def main():
    logging.basicConfig(level=logging.INFO)
    config = configparser.ConfigParser()
    config.read_file(open("settings.ini"))

    logging.info('Started work')

    main_coin = config['decimal']['main_coin']
    address_to_link = config['decimal']['address_to_link']
    dec = DecimalApi(config)
    telegram = TelegramApi(config, logging)
    tabulation = '{0:<10} {1}\n'
    tabulation_with_coin = '{0:<10} {1} {2}\n'

    while True:
        latest_parsed_block = latestBlock.read()
        block = dec.actual_block()

        if not latest_parsed_block:
            latestBlock.write(block)

        if latest_parsed_block and latest_parsed_block < block:

            logging.info('Latest parsed block {}: '.format(latest_parsed_block))

            block = min(block, latest_parsed_block + 1) if latest_parsed_block else block

            logging.info('Block to parse: {}'.format(block))

            txs = dec.block_txs(block)
            if txs['count'] > 0:
                for tx in txs['txs']:
                    tx_hash = tx['hash']
                    text = ''

                    if tx['type'] == 'create_coin':
                        coin = dec.coin(tx['data']['symbol'])
                        coin_name = tx['data']['symbol'].upper()
                        creator = coin['coin']['creator']
                        balance_del = dec.balance(creator)
                        crr = str(coin['coin']['crr']) + '%'
                        reserve = round(float(coin['coin']['reserve']), 2)
                        max_supply = int(tx['data']['limit_volume']) * 0.000000000000000001
                        price = round(float(coin['initial']['price']), 2)

                        text += '➕ [{}]({}/coins/{}) \[coin] {}, {} {}\n'.format(
                            coin_name, address_to_link, coin_name, crr, dec.reserve_to_title(reserve), coin_name)
                        text += '`'
                        text += tabulation.format("Type", "Coin")
                        text += tabulation.format('Name', coin_name)
                        text += tabulation.format('CRR', crr)
                        text += tabulation_with_coin.format('Price', price, main_coin.upper())
                        text += tabulation_with_coin.format('Supply', coin['initial']['volume'], coin_name)
                        text += tabulation_with_coin.format('Max supply', int(max_supply), coin_name)
                        text += tabulation_with_coin.format('Reserve', reserve, main_coin.upper())
                        text += '`'
                        text += '\n'
                        text += '🙎‍♂ Creator: \n'
                        text += '[{}]({}/address/{})\n'.format(creator, address_to_link, creator)
                        text += '`'
                        text += tabulation.format('Balance', balance_del)
                        text += '`'

                        logging.info('Founded create_coin tx, tx_hash: {}'.format(tx_hash))

                        telegram.send_notify(text.strip(), tx_hash)

                    if tx['type'] == 'mint_nft':
                        try:
                            nft_token = dec.nft_token(tx['data']['nft']['tokenUri'])
                        except requests.exceptions.ConnectionError as error:
                            logging.error(error)

                        if 'nft_token' not in locals():
                            nft_token = {'headline': 'No name', 'cover': None}

                        reserve = int(tx['data']['nft']['reserve']) * 0.000000000000000001
                        creator = tx['data']['nft']['creator']
                        balance_del = dec.balance(creator)

                        text += '➕ [{}]({}/transactions/{}) \[NFT] {} {}\n' \
                            .format(nft_token['headline'], address_to_link, tx_hash, dec.reserve_to_title(int(reserve)),
                                    main_coin.upper())
                        text += '`'
                        text += tabulation.format("Type", "NFT")
                        text += tabulation.format('Name', nft_token['headline'])
                        text += tabulation_with_coin.format('Reserve', str(int(reserve)), main_coin.upper())
                        text += tabulation.format('Quantity', tx['data']['nft']['quantity'])
                        text += tabulation.format('Collection', tx['data']['nft']['nftCollection'])
                        text += '`'
                        text += '\n'
                        text += '🙎‍♂ Creator: \n'
                        text += '[{}](https://testnet.explorer.decimalchain.com/address/{}) \n'.format(creator, creator)
                        text += '`'
                        text += '{} {}'.format('Balance', balance_del)
                        text += '`'

                        logging.info('Founded mint_nft tx, tx_hash: {}'.format(tx_hash))

                        telegram.send_notify(text.strip(), tx_hash, 'nft', nft_token['cover'])
            else:
                logging.info('Not found txs on block: {}'.format(block))

            latestBlock.write(block)

        else:
            logging.debug('loop')

        sleep(1)


if __name__ == '__main__':
    main()
