from services.data_fetcher import get_coins_data

if __name__ == "__main__":
    # Fetch and prepare coins data
    print("Fetching coins data...")
    coins_data = get_coins_data()

    # Print a summary or process the coins data
    print(f"Fetched data for {len(coins_data)} coins.")