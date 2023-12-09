from bs4 import BeautifulSoup
import convert_numbers
from datetime import datetime
import aiohttp
import asyncio
import time
import matplotlib.pyplot as plt
import json
import os


async def get_gold_price24_async(url, _key):
    """
   This function takes an url and returns the gold price from that url
   :param url:
   :param _key:
   :return: float - the gold price
    """
    try:
        async with (aiohttp.ClientSession() as session):
            async with session.get(url) as response:
                page_content = await response.text()
                soup = BeautifulSoup(page_content, 'html.parser')

                if url == 'https://www.livepriceofgold.com/':
                    gold_price24 = soup.find('div', class_="currencyt-h").find_all('table')[1].find_all('tr')[10]
                    gold_price24 = gold_price24.find_all('td')[1].text.replace("KWD", "").strip()
                    gold_price24 = float(convert_numbers.hindi_to_english(gold_price24)) / 100
                else:
                    gold_price24 = soup.find_all('tbody')[0].find_all('tr')[0].find_all('td')[1]
                    gold_price24 = gold_price24.text.replace("د.ك.", "").replace("\xa0\u200f", "")
                    if url == 'https://wikigerman.net/gold-kw/':
                        gold_price24 = float(convert_numbers.hindi_to_english(gold_price24)) / 100
                    else:
                        gold_price24 = float(convert_numbers.hindi_to_english(gold_price24)) / 1000

                return gold_price24, _key, url

    except Exception as e:
        print(f'Error fetching data from the website {url} and the error is: {e} ')
        return None


def update_gold_price24_json_file(average_gold_price):
    """
    This function takes the average gold price and updates the gold_prices.json file
    :param average_gold_price:
    :return: None
    """
    print('\nUpdating the gold_prices.json file .......', end='')

    if os.path.exists('gold_prices.json'):
        with open('gold_prices.json', 'r') as file:
            data = json.load(file)
            new_update = {
                'date': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                'price': average_gold_price
            }

            data.append(new_update)

        with open('gold_prices.json', 'w') as file:
            json.dump(data, file, indent=4)

    else:
        with open('gold_prices.json', 'w') as file:
            new_update = {
                'date': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                'price': average_gold_price
            }
            json.dump([new_update], file, indent=4)

    print(' Done')


async def get_silver_price_async(url, _key):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.google.com/',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-User': '?1',
        'Connection': 'keep-alive',
    }

    params = {
        'currency': 'KWD',
        'amount': '1',
    }

    div_class = None

    if url == 'https://www.livepriceofgold.com/silver-price/kuwait.html':
        div_class = "sekme-content"

    elif url == 'https://www.prokerala.com/finance/silver-price.php':
        div_class = "highlight highlight-blue"

    try:
        async with (aiohttp.ClientSession() as session):
            async with session.get(url, params=params, headers=headers) as response:
                page_content = await response.text()

                soup = BeautifulSoup(page_content, 'html.parser')
                silver_prices_data = soup.find_all('div', class_=div_class)[0]
                silver_price = silver_prices_data.find_all('tr')[1]
                silver_price = silver_price.find_all('td')[1].text.replace("KWD", "").strip()

                if silver_price:
                    return float(silver_price), _key, url
                else:
                    print(f'Error fetching data from the website {url}')
                    return None

    except Exception as e:
        print(f'Error fetching data from the website {url} and the error is: {e} ')
        return None


def update_silver_price999_json_file(average_silver_price):
    """
    This function takes the average silver price and updates the silver_prices.json file
    :param average_silver_price:
    :return: None
    """
    print('\nUpdating the silver_prices.json file .......', end='')

    if os.path.exists('silver_prices.json'):
        with open('silver_prices.json', 'r') as file:
            data = json.load(file)
            new_update = {
                'date': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                'price': average_silver_price
            }

            data.append(new_update)

        with open('silver_prices.json', 'w') as file:
            json.dump(data, file, indent=4)

    else:
        with open('silver_prices.json', 'w') as file:
            new_update = {
                'date': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                'price': average_silver_price
            }
            json.dump([new_update], file, indent=4)

    print(' Done')


async def get_all_stock_prices(stock_dict):

    stock_prices = []
    tasks = []
    print()
    start = time.time()

    for key, value in stock_dict.items():
        urls = value[0]
        _function = value[1]
        for url in urls:
            tasks.append(asyncio.create_task(_function(url, key)))

    done, pending = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)

    for t in done:
        if t.result():
            stock_price = t.result()[0]
            stock_type = t.result()[1]
            stock_url = t.result()[2]
            stock_prices.append((stock_price, stock_type, stock_url))

    end = time.time()
    # get the average price in 3 decimal points
    if stock_prices:

        gold_prices = [(stock_price[0], stock_price[2]) for stock_price in stock_prices if stock_price[1] == "Gold"]
        average_gold_price = round(sum([gold_price[0] for gold_price in gold_prices]) / len(gold_prices), 3)

        for price, url in gold_prices:
            print(f'The gold price from website: {url} {" " * (54 - len(url))} is {price} KD')

        print(f'\nThe average gold price is: {average_gold_price} KD')

        print()
        silver_prices = [(stock_price[0], stock_price[2]) for stock_price in stock_prices if stock_price[1] == "Silver"]
        average_silver_price = round(sum([silver_price[0] for silver_price in silver_prices]) / len(silver_prices), 3)

        for price, url in silver_prices:
            print(f'The silver price from website: {url} {" " * (56 - len(url))} is {price} KD')

        print(f'\nThe average silver price is: {average_silver_price} KD')

        print(f'\nTime taken: {end - start}')
        return average_gold_price, average_silver_price
    else:
        print(f'Error fetching data from the websites')
        return None


def plot_prices():
    # plot the data in a graph
    try:
        with open('gold_prices.json', 'r') as file:
            data = json.load(file)
            # Extract dates and prices
            dates = [datetime.strptime(entry['date'], '%d/%m/%Y %H:%M:%S') for entry in data]
            prices = [entry['price'] for entry in data]

            # Plotting
            plt.figure(figsize=(10, 6))
            plt.plot(dates, prices, marker='o', linestyle='-', color='b')
            plt.title('Gold Prices Over Time')
            plt.xlabel('Date and Time')
            plt.ylabel('Gold Price')
            plt.xticks(rotation=90)

            # view grid
            plt.grid(True)

            # Set x-axis tick frequency
            every_n_ticks = len(dates) // 20  # Adjust this value to show more or fewer dates
            plt.gca().xaxis.set_major_locator(plt.MaxNLocator(nbins=len(dates) // every_n_ticks))

            plt.tight_layout()
            plt.savefig('gold_prices.png')
            plt.show()

    except Exception as e:
        print(f'Error plotting the data: {e}')
