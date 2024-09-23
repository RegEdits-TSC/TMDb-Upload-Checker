from utils import fetch_site_data, output_site_results
from rich.progress import Progress, BarColumn, TimeElapsedColumn, TimeRemainingColumn, ProgressColumn
from rich.live import Live
from rich.console import Console
import time

console = Console()

# Custom column for task description with bold color change based on progress
class CustomTaskDescriptionColumn(ProgressColumn):
    def render(self, task):
        color = "bold bright_green" if task.percentage == 100 else "bold bright_yellow"
        description = "Finished Checking TMDb ID(s)... " if task.percentage == 100 else "Checking TMDb ID(s)... "
        return f"[{color}]{description}[/]"

# Custom column for percentage complete with bold color (yellow until 100%, then green)
class CustomPercentageColumn(ProgressColumn):
    def render(self, task):
        percentage = task.percentage
        color = "bold bright_green" if percentage == 100 else "bold bright_yellow"
        return f"[{color}]{percentage:>3.0f}%[/]"

# Custom Time Remaining Column with bold color (yellow until task completes, then green shows "Completed")
class CustomTimeRemainingColumn(TimeRemainingColumn):
    def render(self, task):
        if task.finished:
            return f"[bold bright_green]Completed[/]"
        else:
            return f"[bold bright_yellow]{super().render(task)}[/]"

# Custom Time Elapsed Column with bold color (yellow until task completion, then green)
class CustomTimeElapsedColumn(TimeElapsedColumn):
    def render(self, task):
        if task.finished:
            color = "bold bright_green"
        else:
            color = "bold bright_yellow"
        return f"[{color}]{super().render(task)}[/]"

# Progress with corrected time remaining logic
def progress_bar(iterations, tmdb_ids_titles, sites, search_type, failed_sites, processed_tmdb_ids, mode, tmdb_ids=None, search=False, search_string=None):
    # Set up the progress bar with custom columns
    progress = Progress(
        CustomTaskDescriptionColumn(),  # Task description with bold yellow-to-green transition
        BarColumn(bar_width=None, complete_style="bold bright_yellow", finished_style="bold bright_green", pulse_style="bright_red"),
        CustomPercentageColumn(),  # Custom percentage column with bold yellow-to-green transition
        CustomTimeRemainingColumn(),  # Custom time remaining column with bold yellow-to-green transition
        CustomTimeElapsedColumn(),  # Custom time elapsed column with bold yellow-to-green transition
    )

    # Use Live to keep the progress bar fixed at the bottom of the screen
    with Live(progress, refresh_per_second=1, console=progress.console):
        check_ids = progress.add_task("Processing...", total=iterations)
        for i in range(iterations):
            if mode == 'json':
                tmdb_id, title = tmdb_ids_titles[i]
                params = {'tmdbId': tmdb_id}

                # Print messages above the progress bar
                progress.console.print(f"[bold bright_green]Searching for TMDb ID: {tmdb_id} (Title: {title})[/]")
                
                # Simulate fetching site data (replace with actual function call)
                site_results = fetch_site_data(sites, params, search_type, failed_sites)

                # Output results in organized format (replace with actual function call)
                output_site_results(site_results)

                # Add the processed TMDb ID to the list
                processed_tmdb_ids.append(tmdb_id)
            elif mode == 'id':
                tmdb_id = tmdb_ids[i]
                found_entry = next((entry for entry in tmdb_ids_titles if entry[0] == tmdb_id), None)

                if found_entry:
                    tmdb_id, title = found_entry
                    progress.console.print(f"[bold bright_green]Found TMDb ID: {tmdb_id} (Title: {title})[/]")
                    params = {'tmdbId': tmdb_id}

                    # Fetch site data
                    site_results = fetch_site_data(sites, params, search_type, failed_sites, search, search_string)

                    # Output results in organized format
                    output_site_results(site_results)

                    # Add the processed TMDb ID to the list
                    processed_tmdb_ids.append(tmdb_id)
                else:
                    progress.console.print(f"[underline bold bright_red]ERROR: TMDb ID {tmdb_id} not found in the {search_type.capitalize()} TMDb IDs file.[/]")
            progress.update(check_ids, advance=1)