# mygrations

A stateless database migrator via Schema as Code!

## About

`mygrations` is not so much a database migration system as it is "Schema as Code".  Rather than having a migration file dedicated to each change in your database, you describe your database schema via standard `CREATE TABLE` and `INSERT` commands.  `mygrations` can validate your schema both in isolation and against an actual production database, allowing you to make your database migration process fully testable.

The actual database migration process is stateless - no need to add a table to your database to keep track of which migrations have run.  Instead, `mygrations` compares your declared schema against the current schema of your databse, determines the necessary steps to make your database match, and updates your database accordingly.  As a result, updating your database structure with `mygrations` doesn't involve creating additional migration files.  Instead, you simply edit the `CREATE TABLE` command inside the original table definition file to add/remove columns, indexes, or constraints as needed.

The main disadvantage with `mygrations` stems from one of its key advantages (statelessness).  `mygrations` cannot handle stateful operations: renaming tables, renaming columns, moving or transforming data.  The only good way to handle those is by using the same methods as every other migration system out there (i.e. migration files with a record of which have run), and there isn't much point in adding that to this tool.  If you really need that, you're better off using more typical migration tools.

## Installation

```
pip3 install mygrations
```

Then you just need to download and install the mygrations runner. Something like this works:

```
wget 'https://raw.githubusercontent.com/cmancone/mygrations/master/mygrate.py'
chmod a+x mygrate.py
sudo mv mygrate.py /usr/local/bin/mygrate.py
```

Your mileage may vary.

## Command line setup

The calling sequence of the mygration runner is not yet very flexible, requiring you to have your environment setup in a particular way.  Right now it assumes:

1. Your application already has a `.env` file somewhere, containing database credentials
2. You place a `mygrate.conf` file in the same directory as the `.env` file
3. You have a folder (somewhere) in your application that has all your `*.sql` files: ideally one for every table in your system

When you run `mygrate.py` it will read the `mygrate.conf` file in your current directory.  It will also read the contents of your `.env` file, where it expects to find key-value pairs, in particular the connection details to your `MySQL` database.  It is as flexible as possible when reading the syntax of the `.env` file, with the goal that you should not have to make any adjustments to it in order to support `mygrate.py`.  Two pieces of information are pulled out of the `mygrate.conf` file: where to find your database credentials in the `.env` file, and where to find the `*.sql` files that it will be migrating your database to match.

```
/var/www/example.com/.env
/var/www/example.com/mygrate.conf
/var/www/example.com/database/*.sql
```

Your `.env` file presumably already exists for your application to use, and may look like this:

```
DB_HOSTNAME = "localhost"
DB_USERNAME = "app"
DB_PASSWORD = "[Your password here]"
DB_DATABASE = "app"

ANOTHER_CONFIG = "SomeValue"
```

Your `mygrate.conf` file would then look like this:

```
hostname_key = "DB_HOSTNAME"
username_key = "DB_USERNAME"
password_key = "DB_PASSWORD"
database_key = "DB_DATABASE"
env_file = ".env"

files_directory = "database/"
```

To be clear, you don't put your database credentials in your `mygrate.conf` file: instead you simply tell it which keys to grab the database credentials out of from your `.env` file.  This way you can just have one `mygrate.conf` file that works in all environments.  The files directory tells it where to find your `*.sql` files.  You simply specify the location of the directory containing those files, relative to the `mygrate.conf` file.  It will automatically read any `*.sql` files in that directory and use the structure in those files to determine the "truth" of what your database should look like.  Finally, the `env_file` setting tells mygrations where to find your `.env` file.  It should be relative to the location of your `mygrate.conf` file (i.e. `.env` if the file is in the same directory or `sub_directory/.env` if the `.env` file lives in a sub directory relative to the `mygrate.conf` file).

To make things super clear I have created an example repository that is ready to run mygrations.  Instructions [here](https://github.com/cmancone/mygrations_example).

## Command line usage

Currently the system supports 5 modes:

| Mode              | Action                                                                                       |
| ----------------- | -------------------------------------------------------------------------------------------- |
| version (default) | Display the version and license information and exit                                         |
| apply             | Update the database!                                                                         |
| check             | Read all `*.sql` file and report any SQL errors or MySQL 1215 errors                         |
| plan              | Dump a list of MySQL commands that will bring the database up-to-spec with the `*.sql` files |
| plan_export       | Dump a list of data showing how to update the `*.sql` files to match the database            |

Each should be executed by running the mygration command with the desired mode as the first parameter, in the same directory as your `mygrate.conf` file:

```mygrate.py [mode]```

The typical use case would be to run `mygrate.py plan` and inspect the results.  If things seem reasonable then simply  `mygrate.py execute`

## Calling from python

If you happen to be using python then you can call mygrations directly if you prefer.  This allows you to manage the connection to the database yourself (but still requires pymysql).  Here's a quick and dirty example (in lieu of proper documentation):

```
from mygrations.core.commands import execute
import pymysql

connection = pymysql.connect(
    user='[DATABASE_USERNAME]',
    password='[DATABASE_PASSWORD]',
    host='[DATABASE_HOST]',
    database='[DATABASE_NAME]',
    autocommit=False,
    connect_timeout=2,
    cursorclass=pymysql.cursors.DictCursor
)

execute('plan', {'connection': connection, 'sql_files': '/folder/with/sql/files'})
execute('apply', {'connection': connection, 'sql_files': '/folder/with/sql/files'})
```
`sql_files` can be the absolute path to a folder that contains your SQL files, or it can be a string with actual SQL (as always, just separate multiple SQL commands with a semi-colon).

## Advantages

There are plenty of migration tools out there, and many frameworks come with their own.  So why would I write another, and why would anyone setup a new tool if one comes out-of-the-box with their framework of choice?  Because the declarative approach taken by `mygrations` has a number of concrete advantages.

### 1. Database Schema Tests

`mygrations` has a couple main testing modes that grant the equivalent of unit and integration testing for your database schema.  For isolated testing, you can point it to your database schema files and it will parse them, inspect them, and warn you of any schema errors - no actual database is required for this!  It will check for things like foreign key errors, duplicate key names, etc.  This allows you to test your schema without having to actually apply it to a database.

Additionally, `mygrations` can validate a schema against an actual database.  This can pick up more subtle errors before trying to update things.  For instance, it will warn you if your schema will add a unique index on a column with duplicate values, or attempt to disallow nulls on a column that already contains null values.  These sorts of subtle issues can be easy-to-miss before running a database migration, but `mygrations` can detect them before applying changes.

In short, you can add `mygrations` to your CI/CD process right "next" to your usual code tests to ensure that code and database changes can safely deploy together.

### 2. Database structure trackable by version control

In `mygrations` each database is defined by a single `CREATE TABLE` command living in a file.  Adjusting a table's structure means adjusting the `CREATE TABLE` command in the table's definition file.  As a result, if two developers attempt to change the same table in conflicting ways, the conflict will be picked up immediately at merge time by your version control system.  Because normal migration systems put each database change in its own file version control cannot pick up any conflicts.  Instead, conflicting table definitions are not found until after a merge when the next migration is run and an SQL error is generated.  This way, potential conflicts are found much sooner.

### 3. Migration plans

Again, because `mygrations` operates with knowledge of both the current database and the target database, it can present an actual migration plan before making any changes.  This makes it easy for the developer to have one last spot check before making changes, if desired.

### 4. Clear Schemas

Standard migration systems dedicate a file to each change of a database table.  As a result, it is very difficult to figure out what the database structure *should* be simply by looking at the contents of the migration directory.  `mygrations` makes it easier for a developer to look at the database schema files and understand exactly what the database should look like.

### 5. No Migration table

Since `mygrations` works directly with the database structure it doesn't need to keep a history of which migrations it has run.  Instead, it brings your database up-to-spec no matter what state it is in: no more hassle if your migration table somehow gets out of sync with your migration files.

### 6. Roll Forward, Roll Back

Because `mygrations` is stateless it has no concept of forward or backward, and no need to define separate instructions for "do" or "undo".  Whether you are changing branches, rolling back to a previous commit, or simply pull down the latest changes, `mygrations` sees no difference and updates your database just the same.

## Roadmap to 1.0

This is a brand new venture that is a long way from complete.  To give some guidance, here is my target feature list for when version 1.0 will officially be released:

1. Parsing of `CREATE TABLE` and `INSERT` commands and using those as migration definitions (Done)
2. Detailed foreign key error notices (Done)
3. Ability to migrate database to match definitions from any state (Done)
4. Generation of migration commands (Done)
5. Generation of migration files (Done)
6. More flexible methods for credential management (load from environment, specify name of .env file, accept cursor from Python)
7. Checks against a live database
8. Auto install PyMySQL and runner

Currently the system has reached a complete enough state that it is being tested in our real-world systems.
