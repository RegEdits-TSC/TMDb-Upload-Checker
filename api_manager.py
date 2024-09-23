import requests
import time
import json
import os

from rich.console import Console

console = Console()

def load_config(config_file='config.json'):
    console.print(f"[bold bright_yellow]Loading configuration from '{config_file}'...[/]")
    time.sleep(1)
    try:
        with open(config_file, 'r') as file:
            config = json.load(file)
        console.print("[bold bright_green]Configuration successfully loaded.[/]")
        return config
    except FileNotFoundError:
        console.print(f"[underline bold bright_red]ERROR: The configuration file '{config_file}' was not found.[/]")
        exit(1)
    except json.JSONDecodeError as e:
        console.print(f"[underline bold bright_red]ERROR: Failed to parse the configuration file '{config_file}'. JSON error: {str(e)}[/]")
        exit(1)
    except Exception as e:
        console.print(f"[underline bold bright_red]ERROR: An unexpected error occurred while loading the configuration: {str(e)}[/]")
        exit(1)

def validate_config(config):
    console.print("[bold bright_yellow]Validating configuration...[/]")
    required_keys = ['api_keys', 'sites']
    for key in required_keys:
        if key not in config:
            console.print(f"[underline bold bright_red]ERROR: The key '{key}' is missing in the configuration file.[/]")
            exit(1)

    for site_name in config['sites']:
        if site_name not in config['api_keys']:
            console.print(f"[underline bold bright_red]ERROR: API key for '{site_name}' is missing in the 'api_keys' section of the configuration.[/]")
            exit(1)

    time.sleep(1)
    console.print("[bold bright_green]Configuration successfully validated.")

def test_api_key(api_url, headers):
    try:
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            return True  # The API key is valid
        else:
            return False  # The API key is invalid or there's another issue
    except requests.exceptions.RequestException as e:
        console.print(f"[underline bold bright_red]ERROR: Failed to test API key -> {e}[/]")
        return False

def setup_api_keys_and_sites(config):
    # Access the API keys and sites from the validated config
    api_keys = config['api_keys']
    sites = {
        site_name: {
            'url': site_info['url'],
            'headers': {
                'Authorization': f'Bearer {api_keys[site_name]}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            'response': None,
            'has_data': False
        }
        for site_name, site_info in config['sites'].items()
    }
    return api_keys, sites

def send_request(site_name, site_info, params):
    try:
        time.sleep(1)  # Add delay to avoid rate limits
        response = requests.get(site_info['url'], headers=site_info['headers'], params=params)
        return response.json()
    except requests.exceptions.RequestException as e:
        console.print(f"[underline bold bright_red]Error fetching data from {site_name}: {str(e)}[/]")
        return {"error": str(e)}