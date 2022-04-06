import os, os.path
from mygrations.helpers.dotenv import dotenv
from mygrations.helpers.db_credentials import DbCredentials
from mygrations.drivers.pymysql.pymysql import PyMySQL
class Base(object):
    options = None
    config = None
    _config_loaded = False

    def __init__(self, options):
        self.options = options

    def get_driver(self):
        if 'driver' not in self.options:
            if 'connection' in self.options:
                self.options['driver'] = PyMySQL(connection=self.options['connection'])
            else:
                self._load_config()
                self.options['driver'] = PyMySQL(DbCredentials(self.config['env_file'], self.config))
        return self.options['driver']

    def get_sql_files(self):
        if 'sql_files' not in self.options:
            self._load_config()
            self.options['sql_files'] = self.config['files_directory']
        return self.options['sql_files']

    def _load_config(self):
        if self._config_loaded:
            return True

        if 'config' not in self.options:
            raise ValueError(f"Missing required 'config' parameter in options for commands '{self.__class__.__name__}'")

        # load up the mygration configuration (which includes the path to the files we will import)
        # note that self.options['config'] is supposed to contain the filename or absolute path to the
        # mygrations configuration file.  By default, this is called `mygrate.conf`.  In return
        # we get the absolute path to this file, which contains the config we need to do anything from
        # the command line (we shouldn't end up here if called programmatically).

        # this can be slightly confusing because of the mixture of self.config and self.options.  It's a simple
        # difference though: self.options is a dictionary passed in by whoever calls us (probably the command line runner),
        # while self.config is a dictionary containing configuration settings loaded out of the mygrate.conf file.
        config_abs_path = self._resolve_and_check_config_file_path(self.options['config'])
        self.config = dotenv(config_abs_path)
        if 'files_directory' not in self.config:
            raise ValueError(
                "Configuration file is missing 'files_directory' configuration, which should point to the directory containing your *.sql files"
            )
        self.config['files_directory'] = self._relative_to_config_abs_path(
            self.config['files_directory'], config_abs_path
        )

        if 'env_file' not in self.config:
            raise ValueError(
                "Configuration file is missing 'env_file' configuration, which should point to the .env file for your application (so mygrations can fetch database credentials"
            )
        # convert the env file path to an absolute path
        self.config['env_file'] = self._relative_to_config_abs_path(self.config['env_file'], config_abs_path)
        self._config_loaded = True

    def execute(self):
        raise NotImplementedError()

    def _resolve_and_check_config_file_path(self, file_path):
        if not len(file_path):
            raise ValueError('Missing path to configuration file')

        # We want to find the location of the mygrate.conf file.  For the most part expect file_path to literally
        # be `mygrate.conf`, as that is the default sent in by the runner.  However the user could have specified
        # something else.  If we have an absolute path specified then that is the only thing we want to check,
        # and we want to throw an exception if it does not match.  However, if it is not an absolute path we
        # want to search for the given file in current directory or its parents.
        if file_path[0] == '/':
            if not os.path.isfile(file_path):
                raise ValueError("Specified configuration file '%s' does not exist" % file_path)
            return file_path

        directories = ('%s/%s' % (os.getcwd(), file_path)).strip('/').split('/')
        filename = directories.pop()
        ndirectories = len(directories)
        for i in range(ndirectories):
            abs_path = '/%s/%s' % ('/'.join(directories[:ndirectories - i]), filename)
            if os.path.isfile(abs_path):
                return abs_path

        raise ValueError("Could not find configuration file '%s' in current directory or parents" % file_path)

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
