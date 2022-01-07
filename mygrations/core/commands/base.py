import os, os.path
from mygrations.helpers.dotenv import dotenv
from mygrations.helpers.db_credentials import DbCredentials
class Base(object):

    credentials = {}
    config = {}

    def __init__(self, options):

        self.options = options

        if not 'env' in self.options:
            raise ValueError('Missing "env" in options for commands.import_files')

        if not 'config' in self.options:
            raise ValueError('Missing "config" in options for commands.import_files')

        # load up the mygration configuration (which includes the path to the files we will import)
        config_abs_path = self._resolve_and_check_config_file(self.options['config'])
        self.config = dotenv(config_abs_path)
        self.config['files_directory'] = self._relative_to_config_abs_path(
            self.config['files_directory'], config_abs_path
        )
        self.options['env'] = self._relative_to_config_abs_path(self.options['env'], config_abs_path)

        # and load up the database credentials
        self.credentials = DbCredentials(self.options['env'], self.config)

        if not 'files_directory' in self.config:
            raise ValueError('Missing files_directory configuration setting in configuration file')

    def execute(self):
        raise NotImplementedError()

    def _resolve_and_check_config_file(self, file_path):
        if not len(file_path):
            raise ValueError('Missing path to env file')

        # We want to find the location of the mygrate.conf file.  For the most part expect file_path to literally
        # be `mygrate.conf`, as that is the default sent in by the runner.  However the user could have specified
        # something else.  If we have an absolute path specified then that is the only thing we want to check,
        # and we want to throw an exception if it does not match.  However, if it is not an absolute path we
        # want to search for the given file in current directory or its parents.
        if file_path[0] == '/':
            if not os.path.isfile(file_path):
                raise ValueError("Specified env file '%s' does not exist" % file_path)
            return file_path

        directories = ('%s/%s' % (os.getcwd(), file_path)).strip('/').split('/')
        filename = directories.pop()
        ndirectories = len(directories)
        for i in range(ndirectories):
            abs_path = '/%s/%s' % ('/'.join(directories[:ndirectories - i]), filename)
            if os.path.isfile(abs_path):
                return abs_path

        raise ValueError("Could not find env file '%s' in current directory or parents" % file_path)

    def _relative_to_config_abs_path(self, relative_path, config_abs_path):
        # Our file directory and our .env file path should both be relative to the location of the mygrate.conf file.
        # The exact path to the mygrate.conf file can change because it is allowed to be in a parent of the
        # current working directory.  Therefore we need a way to take a relative path and turn it into an absolute
        # path using the absolute path to the configuration file (i.e. the mygrate.conf file).
        # This method does just that.
        # However, don't muck with a path if it already absolute
        if relative_path[0] == '/':
            return relative_path

        return '%s/%s' % (os.path.dirname(config_abs_path), relative_path)
