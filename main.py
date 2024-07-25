import requests
from twilio.rest import Client

# Constants
STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"
STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
STOCK_API_KEY = "YOUR_API_KEY"
NEWS_API_KEY = "YOUR_API_KEY"
TWILIO_SID = "YOUR_SID"
TWILIO_AUTH_TOKEN = "YOUR_AUTH_TOKEN"

# Function to get stock data
def get_stock_data(symbol, api_key):
    stock_params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": api_key
    }
    response = requests.get(STOCK_ENDPOINT, params=stock_params)
    response.raise_for_status()
    return response.json()["Time Series (Daily)"]

# Function to get the closing price
def get_closing_price(data, days_ago):
    data_list = [value for (key, value) in data.items()]
    return float(data_list[days_ago]["4. close"])

# Function to get news articles
def get_news(company_name, api_key):
    news_params = {
        "apiKey": api_key,
        "qInTitle": company_name
    }
    response = requests.get(NEWS_ENDPOINT, params=news_params)
    response.raise_for_status()
    return response.json()["articles"]

# Function to send SMS via Twilio
def send_sms(messages, sid, auth_token, from_number, to_number):
    client = Client(sid, auth_token)
    for message in messages:
        client.messages.create(
            body=message,
            from_=from_number,
            to=to_number
        )

# Main code
stock_data = get_stock_data(STOCK_NAME, STOCK_API_KEY)

# Get closing prices
yesterday_closing_price = get_closing_price(stock_data, 0)
day_before_yesterday_closing_price = get_closing_price(stock_data, 1)

# Calculate the difference and percentage
difference = yesterday_closing_price - day_before_yesterday_closing_price
up_down = "🔺" if difference > 0 else "🔻"
diff_percent = round((abs(difference) / yesterday_closing_price) * 100)

# Check if the percentage difference is greater than 5%
if diff_percent > 5:
    articles = get_news(COMPANY_NAME, NEWS_API_KEY)
    three_articles = articles[:3]
    formatted_articles = [f"{STOCK_NAME}:{up_down}{diff_percent}% \nHeadline: {article['title']}. \nBrief: {article['description']}" for article in three_articles]
    send_sms(formatted_articles, TWILIO_SID, TWILIO_AUTH_TOKEN, "YOUR_TWILIO_NUMBER", "YOUR_NUMBER")
