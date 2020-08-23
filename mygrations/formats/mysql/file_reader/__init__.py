from .reader import reader
from .database import database

def parse(strings):
    return database(strings).as_core_database()
