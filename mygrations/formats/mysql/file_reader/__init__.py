from .reader import Reader
from .database import Database
def parse(strings):
    return Database(strings).as_core_database()
