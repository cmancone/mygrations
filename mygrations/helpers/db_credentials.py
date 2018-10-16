from .dotenv import dotenv
class db_credentials(dict):

    config = {}
    env = {}

    key_map = {'hostname_key': 'host', 'database_key': 'db', 'username_key': 'user', 'password_key': 'passwd'}

    def __init__(self, env, config):

        # Config represents the contents of the mygrate.conf file.
        # env represents the contents of the applications .env file.
        # Normally the config file will tell us which keys in the .env
        # file have the database credentials.
        self.config = config if isinstance(config, dotenv) else dotenv(config)
        self.env = env if isinstance(env, dotenv) else dotenv(env)

        # we need four pieces of information for this to work:
        for key in ['hostname_key', 'username_key', 'password_key', 'database_key']:
            if not key in self.config:
                raise ValueError("Cannot find required key %s in mygrate.conf" % key)

        # now make sure we have it in our .env
        credentials = {}
        for (key, val) in self.key_map.items():

            key_name = self.config[key]
            if not key_name in self.env:
                raise ValueError("Failed to fulfill %s: key %s not found in .env" % (val, key_name))

            credentials[val] = self.env[key_name]

        super().__init__(credentials)
