from django.shortcuts import render

# finance/views.py
from django.http import JsonResponse
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


def any_value_equal_to_threshold(open_price, high_price, low_price, close_price, threshold):
    return open_price == threshold or high_price == threshold or low_price == threshold or close_price == threshold


def get_15min_candles(symbol, start_date, end_date, threshold):
    matching_candles = []
    url = f"https://finance.yahoo.com/quote/{symbol}/history"
    params = {
        'period1': int(start_date.timestamp()),
        'period2': int(end_date.timestamp()),
        'interval': '15m',
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', {'class': 'W(100%) M(0)'})
        if table:
            rows = table.find_all('tr', {'class': 'BdT Bdc($seperatorColor) Ta(end) Fz(s) Whs(nw)'})
            for row in rows:
                cols = row.find_all('td')
                if len(cols) == 7:  # Check if it's a data row
                    timestamp = int(cols[0].span['data-value'])
                    date_time = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                    open_price = float(cols[1].span.text.replace(',', ''))
                    high_price = float(cols[2].span.text.replace(',', ''))
                    low_price = float(cols[3].span.text.replace(',', ''))
                    close_price = float(cols[4].span.text.replace(',', ''))

                    # Check if any OHLC value matches the threshold
                    if any_value_equal_to_threshold(open_price, high_price, low_price, close_price, threshold):
                        matching_candles.append({
                            'timestamp': timestamp,
                            'datetime': date_time,
                            'open': open_price,
                            'high': high_price,
                            'low': low_price,
                            'close': close_price
                        })
    return matching_candles


def fetch_candles(request):
    symbol = request.GET.get('symbol', 'AAPL')
    threshold = float(request.GET.get('threshold', 200))
    end_date = datetime.now()
    start_date = end_date - timedelta(days=1)  # Fetch data for the last 1 day

    candles = get_15min_candles(symbol, start_date, end_date, threshold)
    return JsonResponse({'candles': candles})

