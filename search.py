import os
import sys

LOG_PATH = os.path.expanduser("~/.crumb/history.org")


def search_log(query):
    """
    Search for a given query string within the crumb history log file and print matching entries.

    Args:
        query (str): The search term to look for in the history entries.

    Returns:
        None
    """
    if not os.path.exists(LOG_PATH):
        print("No history file found.")
        return

    with open(LOG_PATH, "r", encoding="utf-8") as f:
        entries = f.read().split("* ")[1:]

    found = 0
    for entry in entries:
        if query.lower() in entry.lower():
            print(f"* {entry.strip()}\n")
            found += 1

    if found == 0:
        print("No matches found.")


if __name__ == "__main__":
    """
    Entry point for the script. Parses command line arguments and calls the search function.
    Usage: search.py <search term>
    """
    if len(sys.argv) < 2:
        print("Usage: search.py <search term>")
    else:
        search_log(sys.argv[1])
