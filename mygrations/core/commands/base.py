from mygrations.helpers.dotenv import dotenv
from mygrations.helpers.db_credentials import db_credentials
class base(object):

    credentials = {}
    config = {}

    def __init__(self, options):

        self.options = options

        if not 'env' in self.options:
            raise ValueError('Missing "env" in options for commands.import_files')

        if not 'config' in self.options:
            raise ValueError('Missing "config" in options for commands.import_files')

        # load up the mygration configuration (which includes the path to the files we will import)
        self.config = dotenv(self.options['config'])

        # and load up the database credentials
        self.credentials = db_credentials(self.options['env'], self.config)

        if not 'files_directory' in self.config:
            raise ValueError('Missing files_directory configuration setting in configuration file')

    def execute(self):
        raise NotImplementedError()
