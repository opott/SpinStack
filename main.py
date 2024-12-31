# SETTINGS
currency_code = "GBP"
currency_symbol = "£"
# END OF SETTINGS

import os
import platform
from time import sleep

import discogs_client
from dotenv import load_dotenv
from pyairtable import Api
from pyairtable.formulas import match
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()

api = Api(os.getenv("AIRTABLE_PAT"))
table = api.table(os.getenv("BASE_ID"), os.getenv("TABLE_ID"))

discogs = discogs_client.Client("SpinStack/0.1", user_token=os.getenv("DISCOGS_TOKEN"))


def clear_console():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")


def main():
    clear_console()
    print("Welcome to SpinStack!")
    print("Please select an option:")
    print("1. Add a new entry")
    print("2. Fetch an existing entry")
    print("3. Edit an existing entry")
    print("4. Delete an existing entry")
    print("5. Update price data")
    print("6. Add a manual entry")

    option = int(input("Enter option number: "))
    if option == 1:
        create_entry()
    elif option == 2:
        fetch_entry()
    elif option == 3:
        edit_entry()
    elif option == 4:
        delete_entry()
    elif option == 5:
        update_price_data()
    elif option == 6:
        create_manual_entry()
    else:
        print("Invalid input. Please try again.")
        main()


def fetch_entry():
    clear_console()
    catalog_number = str(input("Enter catalog number: ")).upper()
    clear_console()
    print("Searching for entry...")
    search_formula = match({"Catalog Number": catalog_number})
    results = table.all(formula=search_formula)
    if not results:
        print("Entry not found.")
    else:
        clear_console()
        for result in results:
            min_price = str(result["fields"]["Min Price"])
            avg_price = str(result["fields"]["Avg Price"])
            max_price = str(result["fields"]["Max Price"])
            print("Catalog Number: " + result["fields"]["Catalog Number"])
            print("Album Name: " + result["fields"]["Album Name"])
            print("Artist Name: " + result["fields"]["Artist Name"])
            print("Min Price: £" + min_price)
            print("Avg Price: £" + avg_price)
            print("Max Price: £" + max_price)
            print("---------------------------------")
            sleep(3)
    again = input("Would you like to fetch another entry? (y/n): ").lower()
    if again == "y":
        fetch_entry()
    else:
        print("Returning to main menu...")
        sleep(2)
        main()


def get_price_data(release_id):
    url = f"https://www.discogs.com/sell/release/{release_id}"

    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

    try:
        driver.get(url)
        sleep(3)

        price_elements = driver.find_elements(
            By.CSS_SELECTOR, 'span.price[data-currency="GBP"]'
        )

        prices = [
            float(price_element.get_attribute("data-pricevalue"))
            for price_element in price_elements
        ]

        if not prices:
            print("No prices found.")
            return 0, 0, 0

        min_price = float(min(prices)) if prices else 0
        max_price = float(max(prices)) if prices else 0
        avg_price = round(sum(prices) / len(prices), 2) if prices else 0

        if len(set(prices)) == 1:
            max_price = min_price

        return min_price, max_price, avg_price

    except Exception:
        print("Error fetching prices...")
        return 0, 0, 0

    finally:
        driver.quit()


def create_entry():
    clear_console()
    catalog_number = str(input("Enter catalog number: ")).upper()
    clear_console()
    print("Searching for release...")
    results = discogs.search(catno=catalog_number).page(1)
    current = results[0]
    release_id = current.id
    title = current.title.split(" - ", 1)[1]
    artist = current.artists[0].name
    print("Release found!")
    print(f"{title} by {artist}")
    correct = str(input("Is this correct? (y/n): ")).lower()

    if correct == "y":
        clear_console()
        print("Fetching price data...")
        print("A browser window will open to fetch the data. Please wait...")
        sleep(1)
        min_price, max_price, avg_price = get_price_data(release_id)
        clear_console()
        print("Price data fetched!")
        print(f"Min: £{min_price}, Max: £{max_price}, Average: £{avg_price}")
        sleep(1)
        print("Creating entry...")
        table.create(
            {
                "Catalog Number": catalog_number,
                "Album Name": title,
                "Artist Name": artist,
                "Max Price": max_price,
                "Avg Price": avg_price,
                "Min Price": min_price,
                "Discogs Release ID": release_id,
                "Discogs Release URL": f"https://www.discogs.com/release/{release_id}",
            }
        )
        print("Entry created!")
    elif correct == "n":
        clear_console()
        print("Let's try again...")
        catalog_number = str(input("Enter catalog number: ")).upper()
        title_search = str(input("Enter album title: "))
        artist_search = str(input("Enter artist name: "))
        clear_console()
        print("Searching for release...")
        results = discogs.search(
            catno=catalog_number, title=title_search, artist=artist_search
        ).page(1)
        current = results[0]
        release_id = current.id
        title = current.title.split(" - ", 1)[1]
        artist = current.artists[0].name
        print("Release found!")
        print(f"{title} by {artist}")
        correct = str(input("Is this correct? (y/n): ")).lower()
        if correct == "y":
            clear_console()
            print("Fetching price data...")
            print("A browser window will open to fetch the data. Please wait...")
            sleep(1)
            min_price, max_price, avg_price = get_price_data(release_id)
            clear_console()
            print("Price data fetched!")
            print(f"Min: £{min_price}, Max: £{max_price}, Average: £{avg_price}")
            sleep(1)
            print("Creating entry...")
            table.create(
                {
                    "Catalog Number": catalog_number,
                    "Album Name": title,
                    "Artist Name": artist,
                    "Max Price": max_price,
                    "Avg Price": avg_price,
                    "Min Price": min_price,
                }
            )
            print("Entry created!")
        elif correct == "n":
            clear_console()
            print(
                "Sorry, I couldn't find the release. You may need to add it manually."
            )
        else:
            print("Invalid input. Please try again.")
            create_entry()
    else:
        print("Invalid input. Please try again.")
        create_entry()

    again = input("Would you like to add another entry? (y/n): ").lower()
    if again == "y":
        create_entry()
    else:
        print("Returning to main menu...")
        sleep(2)
        main()


def edit_entry():
    clear_console()
    catalog_number = str(input("Enter catalog number: ")).upper()
    clear_console()
    print("Searching for entry...")
    search_formula = match({"Catalog Number": catalog_number})
    results = table.all(formula=search_formula)
    if not results:
        print("Entry not found.")
    else:
        clear_console()
        result = results[0]
        entry_id = result["id"]
        min_price = str(result["fields"]["Min Price"])
        avg_price = str(result["fields"]["Avg Price"])
        max_price = str(result["fields"]["Max Price"])
        print("Catalog Number: " + result["fields"]["Catalog Number"])
        print("Album Name: " + result["fields"]["Album Name"])
        print("Artist Name: " + result["fields"]["Artist Name"])
        print("Min Price: £" + min_price)
        print("Avg Price: £" + avg_price)
        print("Max Price: £" + max_price)
        edit = input("Would you like to edit this entry? (y/n): ").lower()
        if edit == "y":
            edit_field(entry_id)
            another_field = input(
                "Would you like to edit another field? (y/n): "
            ).lower()
            if another_field == "y":
                edit_field(entry_id)
            else:
                print("Returning to main menu...")
                sleep(2)
                main()
        else:
            print("Returning to main menu...")
            sleep(2)
            main()


def edit_field(entry_id):
    clear_console()
    print("Select a field to edit:")
    print("1. Catalog Number")
    print("2. Album Name")
    print("3. Artist Name")
    print("4. Min Price")
    print("5. Avg Price")
    print("6. Max Price")
    field = int(input("Enter field number: "))
    if field == 1:
        catalog_number = str(input("Enter new catalog number: ")).upper()
        clear_console()
        print("Updating entry...")
        table.update(entry_id, {"Catalog Number": catalog_number})
        print("Entry updated!")
    elif field == 2:
        album_name = str(input("Enter new album name: "))
        clear_console()
        print("Updating entry...")
        table.update(entry_id, {"Album Name": album_name})
        print("Entry updated!")
    elif field == 3:
        artist_name = str(input("Enter new artist name: "))
        clear_console()
        print("Updating entry...")
        table.update(entry_id, {"Artist Name": artist_name})
        print("Entry updated!")
    elif field == 4:
        min_price = float(input("Enter new min price, excluding currency symbol: "))
        clear_console()
        print("Updating entry...")
        table.update(entry_id, {"Min Price": min_price})
    elif field == 5:
        avg_price = float(input("Enter new avg price, excluding currency symbol: "))
        clear_console()
        print("Updating entry...")
        table.update(entry_id, {"Avg Price": avg_price})
        print("Entry updated!")
    elif field == 6:
        max_price = float(input("Enter new max price, excluding currency symbol: "))
        clear_console()
        print("Updating entry...")
        table.update(entry_id, {"Max Price": max_price})
        print("Entry updated!")


def delete_entry():
    clear_console()
    catalog_number = str(input("Enter catalog number: ")).upper()
    clear_console()
    print("Searching for entry...")
    search_formula = match({"Catalog Number": catalog_number})
    results = table.all(formula=search_formula)
    if not results:
        print("Entry not found.")
    else:
        clear_console()
        result = results[0]
        entry_id = result["id"]
        min_price = str(result["fields"]["Min Price"])
        avg_price = str(result["fields"]["Avg Price"])
        max_price = str(result["fields"]["Max Price"])
        print("Catalog Number: " + result["fields"]["Catalog Number"])
        print("Album Name: " + result["fields"]["Album Name"])
        print("Artist Name: " + result["fields"]["Artist Name"])
        print("Min Price: £" + min_price)
        print("Avg Price: £" + avg_price)
        print("Max Price: £" + max_price)
        delete = input("Would you like to delete this entry? (y/n): ").lower()
        if delete == "y":
            clear_console()
            print("Deleting entry...")
            table.delete(entry_id)
            print("Entry deleted!")
            sleep(2)
            print("Returning to main menu...")
            main()
        else:
            print("Canceling deletion...")
            print("Returning to main menu...")
            sleep(2)
            main()


def update_price_data():
    clear_console()
    print("This may take a while...")
    confirm = str(
        input("Are you sure you want to update the price data? (y/n): ")
    ).lower()
    if confirm == "y":
        records = table.all()
        for record in records:
            release_id = record["fields"]["Discogs Release ID"]
            print(f'Updating price data for {record["fields"]["Album Name"]}...')
            min_price, max_price, avg_price = get_price_data(release_id)
            table.update(
                record["id"],
                {
                    "Max Price": max_price,
                    "Avg Price": avg_price,
                    "Min Price": min_price,
                },
            )
        print("Price data updated!")
        print("Returning to main menu...")
        sleep(2)
        main()
    else:
        print("Returning to main menu...")
        sleep(2)
        main()


def create_manual_entry():
    clear_console()
    catalog_number = str(input("Enter catalog number: ")).upper()
    title = str(input("Enter album title: "))
    artist = str(input("Enter artist name: "))
    release_id = int(input("Enter Discogs release ID: "))
    clear_console()
    print("Fetching price data...")
    print("A browser window will open to fetch the data. Please wait...")
    sleep(1)
    min_price, max_price, avg_price = get_price_data(release_id)
    clear_console()
    print("Price data fetched!")
    print(f"Min: £{min_price}, Max: £{max_price}, Average: £{avg_price}")
    sleep(1)
    print("Creating entry...")
    table.create(
        {
            "Catalog Number": catalog_number,
            "Album Name": title,
            "Artist Name": artist,
            "Max Price": max_price,
            "Avg Price": avg_price,
            "Min Price": min_price,
            "Discogs Release ID": release_id,
            "Discogs Release URL": f"https://www.discogs.com/release/{release_id}",
        }
    )
    print("Entry created!")
    print("Returning to main menu...")
    sleep(2)
    main()


main()
