import time
import requests
import random

from api_manager import validate_config, load_config, setup_api_keys_and_sites, test_api_key
from file_manager import load_tmdb_ids, save_tmdb_ids, get_tmdb_filepath_and_entries
from user_interaction import get_iterations, get_search_type, get_tmdb_mode, get_tmdb_file, removed_parsed_entries, search_for_string, get_search_strings
from utils import get_latest_tmdb_url, extract_tmdb_ids_titles
from progress_bar import progress_bar
from rich.console import Console

console = Console()

# Load the configuration
config = load_config()

# Validate the configuration
validate_config(config)

# Configure API and site information
api_keys, sites = setup_api_keys_and_sites(config)

# List to store site names where the API check fails
failed_sites = []

# Test API keys from config.json
for site_name, site_info in sites.items():
    if test_api_key(site_info['url'], site_info['headers']):
        console.print(f"[bold bright_green]The API key for {site_name} is valid ✅[/]")    
    else:
        console.print(f"[underline bold bright_yellow]WARNING: The API key for {site_name} is invalid or there was an error.[/]")
        failed_sites.append(site_name)

# Check if all sites failed
if len(failed_sites) == len(sites):
    console.print("[underline bold bright_red]ERROR: All API keys failed. The script cannot proceed. Exiting script...[/]")
    exit(1)

# Loop until user wants to stop searching
while True:
    # Determine the search type (Movies or Shows)
    search_type = get_search_type()

    # Load the appropriate TMDb IDs file based on the user's choice
    filepath, tmdb_entries = get_tmdb_filepath_and_entries(search_type)

    # Get the latest URL for downloading TMDb IDs
    download_url = get_latest_tmdb_url(search_type)

    # Check if the file is empty or contains no valid TMDb IDs
    if not tmdb_entries:
        tmdb_entries = get_tmdb_file(search_type, download_url, filepath, load_tmdb_ids)

    # Ask the user if they want to specify a TMDb ID or read from the .json file
    mode = get_tmdb_mode()

    if mode == 'json':
        # Shuffle the entries to randomize the order
        random.shuffle(tmdb_entries)

        # Extract IDs and titles for processing
        tmdb_ids_titles = extract_tmdb_ids_titles(tmdb_entries, search_type)

        # List to track which IDs were successfully processed
        processed_tmdb_ids = []

        # Get the number of iterations the user wants to perform
        iterations = get_iterations(len(tmdb_ids_titles))

        progress_bar(iterations, tmdb_ids_titles, sites, search_type, failed_sites, processed_tmdb_ids, mode)

    elif mode == 'id':
        # Ask for the specific TMDb ID(s)
        console.print("[bold bright_yellow]Enter the TMDb ID(s) you'd like to search for (comma-separated if multiple):[/]", end=" ")
        while True:
            tmdb_ids_input = input().strip()

            # Split the input into a list of TMDb IDs, strip whitespace, and remove duplicates by converting to a set
            tmdb_ids = {tmdb_id.strip() for tmdb_id in tmdb_ids_input.split(',')}

            # Convert the set back to a list of integers for comparison
            try:
                tmdb_ids = [int(tmdb_id) for tmdb_id in tmdb_ids]
                break  # If conversion succeeds, break out of the loop
            except ValueError:
                console.print("[underline bold bright_red]ERROR: All TMDb IDs must be numeric values. Please also ensure there are no leading or trailing commas.[/]", end=" ")

        # Extract IDs and titles for processing
        tmdb_ids_titles = extract_tmdb_ids_titles(tmdb_entries, search_type)

        # List to track which IDs were successfully processed
        processed_tmdb_ids = []

        # Get the number of iterations based on how many TMDb IDs user inputs
        iterations = len(tmdb_ids)

        # Does the user want to search for a specific string
        search = search_for_string()

        # If the user wants to search for a specific string, get the string
        if search:
            search_string = get_search_strings()
            progress_bar(iterations, tmdb_ids_titles, sites, search_type, failed_sites, processed_tmdb_ids, mode, tmdb_ids, search, search_string)
        else:
            progress_bar(iterations, tmdb_ids_titles, sites, search_type, failed_sites, processed_tmdb_ids, mode, tmdb_ids)

    # After processing all TMDb IDs, ask whether to remove them from the .json file
    if processed_tmdb_ids and mode =='json':
        remove_items = removed_parsed_entries()

        if remove_items:
            # Remove processed entries from the list and save the remaining entries back to the file
            console.print("[bold bright_yellow]Removing TMDb ID(s) that have already been searched from the `.json` file to maintain a list of unsearched IDs.[/]")
            tmdb_entries = [entry for entry in tmdb_entries if entry['id'] not in processed_tmdb_ids]  # Remove processed entries
            save_tmdb_ids(filepath, tmdb_entries)
        else:
            console.print("[bold bright_green]TMDb ID entry/entries will remain in the `.json` file and will not be removed.[/]")
    
    console.print("[bold bright_yellow]Would you like to continue searching? (Y/N):[/]", end=" ")

    # Prompt the user whether to continue or stop
    while True:
        continue_search = input().lower().strip()

        if continue_search == 'y':
            break  # Continue with the loop
        elif continue_search == 'n':
            console.print("[bold bright_green]Search process terminated by user.[/]")
            exit()  # Stop the loop and exit
        else:
            console.print("[bold bright_red]Invalid input. Please type 'Y' or 'N'.[/]", end=" ")