import re

from file_manager import download_and_extract_tmdb_ids
from rich.console import Console

console = Console()

def get_iterations(max_iterations):
    console.print(f"[bold bright_yellow]Enter the number of iterations you'd like to perform (Max {max_iterations}):[/]", end=" ")
    while True:
        try:
            iterations = int(input())
            
            if iterations <= 0:
                console.print("[bold bright_red]Please enter a positive number greater than 0.[/]", end=" ")
            elif iterations > max_iterations:
                console.print(f"[bold bright_red]Please enter a number less than or equal to {max_iterations}.[/]", end=" ")
            elif iterations > 50:
                console.print("[underline bold bright_yellow]WARNING: Doing more than 50 iterations can cause issues. Type 'confirm' to proceed or 'back' to change the number:", end=" ")
                warning = input().lower()
                if warning == 'confirm':
                    return iterations
                elif warning != 'back':
                    console.print("[underline bold bright_red]Invalid input. Please type 'confirm' or 'back'.[/]", end=" ")
            else:
                return iterations
                
        except ValueError:
            console.print("[bold bright_red]Please enter a valid positive integer.[/]", end=" ")

def get_search_type():
    console.print("[bold bright_yellow]Would you like to search for Movies or Shows?[/]", end=" ")
    while True:
        search_type = input().strip().lower()
        if search_type in ['movies', 'shows']:
            return search_type
        else:
            console.print("[underline bold bright_red]Invalid input. Please enter 'Movies' or 'Shows'.[/]", end=" ")

def get_tmdb_mode():
    console.print("[bold bright_yellow]Would you like to specify a TMDb ID or read from the '.json' file? (type 'id' or 'json'):[/]", end=" ")
    while True:
        mode = input().strip().lower()
        if mode in ['id', 'json']:
            return mode
        else:
            console.print("[bold bright_red]Invalid input. Please type 'id' to specify a TMDb ID or 'json' to read from the '.json' file.[/]", end=" ")

def get_tmdb_file(search_type, download_url, filepath, load_tmdb_ids):
    console.print(f"[underline bold bright_red]The {search_type.capitalize()} TMDb IDs file is either empty or missing. Please download a new file.[/]")
    console.print("[bold bright_yellow]Would you like to download the latest TMDb IDs file? (Y/N):[/]", end=" ")
    while True:
        download = input().strip().lower()
        if download == 'y':
            download_and_extract_tmdb_ids(download_url, filepath)
            tmdb_entries = load_tmdb_ids(filepath)
            if not tmdb_entries:
                console.print(f"[underline bold bright_red]ERROR: Failed to download or load the {search_type.capitalize()} TMDb IDs file. Exiting...[/]")
                exit(1)
            break
        elif download == 'n':
            console.print("[bold bright_red]Exiting script...[/]")
            exit(1)
        else:
            console.print("[bold bright_red]Invalid input. Please type 'Y' or 'N'.[/]", end=" ")
    return tmdb_entries

def removed_parsed_entries():
    console.print("[bold bright_yellow]Would you like to remove the recently parsed TMDb ID(s) from the '.json' file? (Y/N):[/]", end=" ")
    while True:
        answer = input().strip().lower()
        if answer == 'y':
            return True
        elif answer == 'n':
            return False
        else:
            console.print("[bold bright_red]Invalid input. Please type 'Y' or 'N'.[/]", end=" ")

def get_search_strings():
    # Prompt the user to enter multiple search strings separated by commas
    console.print("[bold bright_yellow]Enter one or more search terms, separated by commas (letters, numbers, and spaces only):[/]")
    console.print("[bold bright_green]TIP: Use '^' between terms for an AND search.[/]")
    while True:
        user_input = input()
        
        # Split the input by commas and strip leading/trailing spaces
        search_strings = [s.strip() for s in user_input.split(',')]

        # Validate each search string using a regular expression
        all_valid = True
        for s in search_strings:
            if not re.match("^[a-zA-Z0-9 ^]+$", s):
                all_valid = False
                break
        
        if all_valid:
            return search_strings  # Return the list of valid search strings
        else:
            console.print("[bold bright_red]Invalid input. Each string must contain only letters, numbers, and spaces.[/]", end=" ")

def search_for_string():
    console.print("[bold bright_yellow]Would you like to search for a specific string? (Y/N):[/]", end=" ")
    while True:
        answer = input().strip().lower()
        if answer == 'y':
            return True
        elif answer == 'n':
            return False
        else:
            console.print("[bold bright_red]Invalid input. Please type 'Y' or 'N'.[/]", end=" ")