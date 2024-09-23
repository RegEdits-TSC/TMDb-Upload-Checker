import time
import pytz
import requests

from api_manager import send_request
from file_manager import save_json_response
from datetime import datetime, timedelta
from rich.console import Console
from rich.text import Text

console = Console()

def output_site_results(site_results):
    # Iterate through site_results in alphabetical order of site_name
    for site_name, results in sorted(site_results.items()):
        # Print the site name in bold yellow
        console.print(f"[bold bright_yellow]{site_name}:[/]")
        
        # Sort the results alphabetically based on the plain text content
        for result in sorted(results, key=lambda x: x.plain):
            console.print(result)  # Print the formatted Text object
        
        console.print()  # Print a blank line for spacing

def bytes_to_gib(size_in_bytes):
    return size_in_bytes / (1024 ** 3)

def get_latest_tmdb_url(search_type):
    current_time_utc = datetime.now(pytz.utc)
    release_time = current_time_utc.replace(hour=8, minute=0, second=0, microsecond=0)

    if current_time_utc < release_time:
        date_for_url = (current_time_utc - timedelta(days=1)).strftime('%m_%d_%Y')
    else:
        date_for_url = current_time_utc.strftime('%m_%d_%Y')

    if search_type == 'movies':
        return f"http://files.tmdb.org/p/exports/movie_ids_{date_for_url}.json.gz"
    else:
        return f"http://files.tmdb.org/p/exports/tv_series_ids_{date_for_url}.json.gz"
    
def fetch_site_data(sites, params, search_type, failed_sites, search=False, search_string=None):
    site_results = {}

    for site_name, site_info in sites.items():
        if site_name in failed_sites:
            continue  # Skip the site if it's in the failed_sites list

        try:
            # Send request to site for torrent information
            sites[site_name]['response'] = send_request(site_name, site_info, params)

            # Save the JSON response to a file for inspection (DEBUG ONLY)
            #save_json_response(site_name, sites[site_name]['response'])

            if sites[site_name]['response'] and 'data' in sites[site_name]['response']:
                sites[site_name]['has_data'] = True
                site_results[site_name] = []
                for item in sites[site_name]['response'].get('data', []):
                    # Define valid categories based on the search type
                    valid_categories = {
                        'movies': ["movie", "movies"],
                        'shows': ["tv show", "tv shows", "tv"]
                    }

                    category = item['attributes'].get('category', '').lower()

                    # Check if the category is valid for the search type
                    if category in valid_categories.get(search_type, []):
                        media_name = item['attributes'].get('name', 'Unknown')
                        if search and search_string:
                            media_name = search_media_names(media_name, search_string)
                            # Check if media_name is not None (or if it's a truthy value like a non-empty list)
                            if not media_name:
                                continue # Skip entries that do not match the search string
                    else:
                        continue  # Skip entries that do not match the search type
                    
                    media_type = item['attributes'].get('type', 'Unknown')
                    resolution = item['attributes'].get('resolution', 'Unknown')
                    size_in_bytes = item['attributes'].get('size', 0)
                    size_in_gib = bytes_to_gib(size_in_bytes)
                    seeders = item['attributes'].get('seeders', 'Unknown')
                    leechers = item['attributes'].get('leechers', 'Unknown')
                    freeleech = item['attributes'].get('freeleech', 'Unknown')

                    # Check if torrent is freelech or if value is defined in .json
                    is_freeleech = freeleech != "0%" and freeleech != "Unknown"
                    freeleech_star = f" ⭐ {freeleech}" if is_freeleech else ""

                    # Assuming site_results is a dictionary or list
                    result = Text()
                    result.append(f"{media_name}", style="bold bright_green")
                    result.append(" ➤ ", style="bright_white")
                    result.append(f"{size_in_gib:.2f} GiB {media_type} ({resolution}) S-{seeders}/L-{leechers}{freeleech_star}", style="bold bright_yellow")

                    # Storing the result in a dictionary/list
                    site_results[site_name].append(result)

            # If no relevant entries found, add "No data found"
            if not site_results.get(site_name):
                result = Text()
                result.append("No data found", style="bold bright_red")
                site_results[site_name].append(result)
        except requests.exceptions.RequestException as e:
            console.print(f"[bold bright_red]Error fetching data from {site_name}: {str(e)}[/]")
            site_results[site_name] = [f"Error fetching data: {str(e)}"]
            continue

    return site_results

def extract_tmdb_ids_titles(tmdb_entries, search_type):
    if search_type == 'movies':
        return [(entry['id'], entry.get('original_title', 'Unknown Title')) for entry in tmdb_entries]
    elif search_type == 'shows':
        return [(entry['id'], entry.get('original_name', 'Unknown Title')) for entry in tmdb_entries]

def search_media_names(media_name, search_strings):
    # Iterate through the list of search strings
    for search_string in search_strings:
        # Split by the ^ symbol to handle AND conditions
        and_conditions = search_string.split('^')

        # Check if all parts of the AND condition exist in media_name
        all_match = True
        for part in and_conditions:
            # Convert to lowercase for case-insensitive search
            part = part.strip().lower()
            if part not in media_name.lower():
                all_match = False
                break
        
        # If all conditions in this search_string match, return the media_name
        if all_match:
            return media_name

    # If no match is found, return None
    return None