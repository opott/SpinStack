import os
import platform
from pyairtable import Api
from pyairtable.formulas import match
import discogs_client
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep

load_dotenv()

api = Api(os.getenv('AIRTABLE_PAT'))
table = api.table(os.getenv('BASE_ID'), os.getenv('TABLE_ID'))

discogs = discogs_client.Client('SpinStack/0.1',
                                user_token=os.getenv('DISCOGS_TOKEN'))

def clear_console():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def main():
    clear_console()
    print('Welcome to SpinStack!')
    print('Please select an option:')
    print('1. Add a new entry')
    print('2. Fetch an existing entry')

    option = int(input('Enter option number: '))
    if option == 1:
        create_entry()
    elif option == 2:
        fetch_entry()
    else:
        print('Invalid input. Please try again.')
        main()

def fetch_entry():
    clear_console()
    catalog_number = str(input('Enter catalog number: ')).upper()
    clear_console()
    print('Searching for entry...')
    search_formula = match({'Catalog Number': catalog_number})
    results = table.all(formula=search_formula)
    if not results:
        print('Entry not found.')
    else:
        clear_console()
        for result in results:
            min_price = str(result['fields']['Min Price'])
            avg_price = str(result['fields']['Avg Price'])
            max_price = str(result['fields']['Max Price'])
            print('Catalog Number: ' + result['fields']['Catalog Number'])
            print('Album Name: ' + result['fields']['Album Name'])
            print('Artist Name: ' + result['fields']['Artist Name'])
            print('Min Price: £' + min_price)
            print('Avg Price: £' + avg_price)
            print('Max Price: £' + max_price)
            print('---------------------------------')
            sleep(3)
    again = input('Would you like to fetch another entry? (y/n): ').lower()
    if again == 'y':
        fetch_entry()
    else:
        print('Returning to main menu...')
        sleep(2)
        main()

def get_price_data(release_id):
    url = f'https://www.discogs.com/sell/release/{release_id}'

    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                              options=options)

    try:
        driver.get(url)
        sleep(3)

        price_elements = driver.find_elements(
            By.CSS_SELECTOR, 'span.price[data-currency="GBP"]')

        prices = []
        for price_element in price_elements:
            price_value = price_element.get_attribute('data-pricevalue')
            prices.append(price_value)

        prices = [float(price) for price in prices]

        max_price = float(max(prices))
        min_price = float(min(prices))
        avg_price = round(sum(prices) / len(prices), 2)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()
        return min_price, max_price, avg_price


def create_entry():
    clear_console()
    catalog_number = str(input('Enter catalog number: ')).upper()
    clear_console()
    print('Searching for release...')
    results = discogs.search(catno=catalog_number).page(1)
    current = results[0]
    release_id = current.id
    title = current.title.split(' - ', 1)[1]
    artist = current.artists[0].name
    print('Release found!')
    print(f'{title} by {artist}')
    correct = str(input('Is this correct? (y/n): ')).lower()

    if correct == 'y':
        clear_console()
        print('Fetching price data...')
        print('A browser window will open to fetch the data. Please wait...')
        sleep(1)
        min_price, max_price, avg_price = get_price_data(release_id)
        clear_console()
        print('Price data fetched!')
        print(f'Min: £{min_price}, Max: £{max_price}, Average: £{avg_price}')
        sleep(1)
        print('Creating entry...')
        table.create({
            'Catalog Number': catalog_number,
            'Album Name': title,
            'Artist Name': artist,
            'Max Price': max_price,
            'Avg Price': avg_price,
            'Min Price': min_price
        })
        print('Entry created!')
    elif correct == 'n':
        clear_console()
        print('Let\'s try again...')
        catalog_number = str(input('Enter catalog number: ')).upper()
        title_search = str(input('Enter album title: '))
        artist_search = str(input('Enter artist name: '))
        clear_console()
        print('Searching for release...')
        results = discogs.search(catno=catalog_number,
                                 title=title_search,
                                 artist=artist_search).page(1)
        current = results[0]
        release_id = current.id
        title = current.title.split(' - ', 1)[1]
        artist = current.artists[0].name
        print('Release found!')
        print(f'{title} by {artist}')
        correct = str(input('Is this correct? (y/n): ')).lower()
        if correct == 'y':
            clear_console()
            print('Fetching price data...')
            print(
                'A browser window will open to fetch the data. Please wait...')
            sleep(1)
            min_price, max_price, avg_price = get_price_data(release_id)
            clear_console()
            print('Price data fetched!')
            print(
                f'Min: £{min_price}, Max: £{max_price}, Average: £{avg_price}')
            sleep(1)
            print('Creating entry...')
            table.create({
                'Catalog Number': catalog_number,
                'Album Name': title,
                'Artist Name': artist,
                'Max Price': max_price,
                'Avg Price': avg_price,
                'Min Price': min_price
            })
            print('Entry created!')
        elif correct == 'n':
            clear_console()
            print(
                'Sorry, I couldn\'t find the release. You may need to add it manually.'
            )
        else:
            print('Invalid input. Please try again.')
            create_entry()
    else:
        print('Invalid input. Please try again.')
        create_entry()


    again = input('Would you like to add another entry? (y/n): ').lower()
    if again == 'y':
        create_entry()
    else:
        print('Returning to main menu...')
        sleep(2)
        main()

main()
