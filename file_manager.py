import json
import requests
import gzip
import shutil
import os

from rich.console import Console

console = Console()

def save_json_response(site_name, response_data):
    filename = f"{site_name}_response.json"
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(response_data, file, ensure_ascii=False, indent=4)
    console.print(f"[bold bright_green]Saved {site_name} response to {filename}[/]")

def get_tmdb_filepath_and_entries(search_type):
    filepath = 'movies_tmdb_ids.json' if search_type == 'movies' else 'shows_tmdb_ids.json'
    tmdb_entries = load_tmdb_ids(filepath)
    return filepath, tmdb_entries

def load_tmdb_ids(filepath):
    tmdb_ids = []
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            for line in file:
                try:
                    data = json.loads(line)
                    tmdb_ids.append(data)  # Keep entire entry for later use
                except json.JSONDecodeError:
                    console.print(f"[underline bold bright_red]ERROR: Failed to decode JSON for line: {line}[/]")
    except FileNotFoundError:
        console.print(f"[bold bright_red]ERROR: File {filepath} not found.[/]")
    return tmdb_ids

def save_tmdb_ids(filepath, tmdb_ids):
    try:
        with open(filepath, 'w', encoding='utf-8') as file:
            for entry in tmdb_ids:
                file.write(json.dumps(entry, ensure_ascii=False) + '\n')
        console.print(f"[bold bright_green]Successfully saved TMDb IDs to {filepath}[/]")
    except IOError as e:
        console.print(f"[underline bold bright_red]ERROR: Failed to save TMDb IDs to {filepath}. {str(e)}[/]")

def download_and_extract_tmdb_ids(url, output_file):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            gz_file = output_file + ".gz"
            with open(gz_file, 'wb') as file:
                file.write(response.content)
            with gzip.open(gz_file, 'rb') as f_in:
                with open(output_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            os.remove(gz_file)
            console.print(f"[bold bright_green]Successfully downloaded and extracted {output_file}[/]")
        else:
            console.print(f"[underline bold bright_red]ERROR: Failed to download file from {url}. Status code: {response.status_code}[/]")
    except requests.exceptions.RequestException as e:
        console.print(f"[underline bold bright_red]ERROR: Failed to download file from {url}. Exception: {str(e)}[/]")