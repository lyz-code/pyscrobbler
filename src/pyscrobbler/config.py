"""Define the configuration of the main program."""

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Configure the pyscrobbler application."""

    verbose: bool = True
    database_url: str = "tinydb://~/.local/share/pyscrobbler/database.tinydb"
