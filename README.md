[![Build Status](https://travis-ci.org/cmancone/mygrations.svg?branch=master)](https://travis-ci.org/cmancone/mygrations)

# mygrations

A general purpose migration tool for managing MySQL updates.  Written in python but intended for use in other systems as well, especially PHP.

## About

`mygrations` manages database migrations with a declarative approach.  Rather than having many migration files, each table in your database has one SQL file which contains a `CREATE TABLE` command that gives the table definition.  This file defines the table structure that you want your table to have (potentially with records as well).  When it comes time to migrate your database, `mygrations` parses the SQL in these files to determine what the structure of your database should be.  It then compares this to the actual table structure in MySQL to determine all of the changes that need to happen to bring the database up to spec.  Finally, it generates any necessary `ALTER TABLE`, `CREATE TABLE`, or `DROP TABLE` commands to update the database.

When you need to change a table structure you don't generate additional migration files, but instead simply edit the `CREATE TABLE` command inside the original table definition file.  When migrating multiple tables related via foreign key constraints you simply have to define your foreign keys in the `CREATE TABLE` command normally.  `mygrations` will take note of the foreign keys and and automatically calculate and resolve dependencies while migrating.

## Installation

1. Requires Python3
2. Requires [MySQLdb For python3](https://pypi.python.org/pypi/mysqlclient).  (For ubuntu: `sudo apt-get install python3-mysqldb`)

To install `mygrations`:

```pip install mygrations```

Then you just need to download and install the mygrations runner.  Something like this works:

```bash
wget 'https://raw.githubusercontent.com/cmancone/mygrations/master/mygrate.py'
chmod a+x mygrate.py
sudo mv mygrate.py /usr/local/bin/mygrate.py
```

Your mileage may vary.

## Setup

The calling sequence of the mygration runner is not yet very flexible, requiring you to have your environment setup in a particular way.  Right now it assumes:

1. Your application already has a `.env` file somewhere, containing database credentials
2. You place a `mygrate.conf` file in the same directory as the `.env` file
3. You have a folder (somewhere) in your application that has all your `*.sql` files: ideally one for every table in your system

When you run `mygrate.py` it will read the `mygrate.conf` file in your current directory.  It will also read the contents of your `.env` file, where it expects to find key-value pairs, in particular the connection details to your `MySQL` database.  It is as flexible as possible when reading the syntax of the `.env` file, with the goal that you should not have to make any adjustments to it in order to support `mygrate.py`.  Two pieces of information are pulled out of the `mygrate.conf` file: where to find your database credentials in the `.env` file, and where to find the `*.sql` files that it will be migrating your database to match.

```
/var/www/example.com/.env
/var/www/example.com/mygrate.conf
/var/www/example.com/public/
/var/www/example.com/database/*.sql
```

Your `.env` file presumably already exists for your application to use, and may look like this:

```
DB_HOSTNAME     = "localhost"
DB_USERNAME     = "app"
DB_PASSWORD     = "[Your password here]"
DB_DATABASE     = "app"

ANOTHER_CONFIG  = "SomeValue"
```

Your `mygrate.conf` file would then look like this:

```
hostname_key    = "DB_HOSTNAME"
username_key    = "DB_USERNAME"
password_key    = "DB_PASSWORD"
database_key    = "DB_DATABASE"

files_directory = "database/"
```

To be clear, you don't put your database credentials in your `mygrate.conf` file: instead you simply tell it which keys to grab the database credentials out of from your `.env` file.  This way you can just have one `mygrate.conf` file that works in all environments.  The files directory tells it where to find your `*.sql` files.  You simply specify the location of the directory containing those files, relative to the `mygrate.conf` file.  It will automatically read any `*.sql` files in that directory and use the structure in those files to determine the "truth" of what your database should look like.

## Usage

Currently the system supports 3 modes:

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

## Advantages

There are plenty of migration tools out there, and many frameworks come with their own.  So why would I write another, and why would anyone setup a new tool if one comes out-of-the-box with their framework of choice?  Because the declarative approach taken by `mygrations` has a number of concrete advantages.

**1. Database structure trackable by version control**

In `mygrations` each database is defined by a single `CREATE TABLE` command living in one file.  Adjusting a table's structure means adjusting the `CREATE TABLE` command in the table's definition file.  As a result, if two developers attempt to change the same table in conflicting ways, the conflict will be picked up immediately at merge time by your version control system.  Because normal migration systems put each database change in its own file version control cannot pick up any conflicts.  Instead, conflicting table definitions are not found until after a merge when the next migration is run and an SQL error is generated.  This way, potential conflicts are found much sooner.

**2. MySQL Linting**

Unlike normal migration systems which simply apply developer-provided transformations to update your tables, `mygrations` is an intelligent tool that understands the actual structure you are trying to create.  As a result it is possible to perform checks to find easy-to-miss syntax errors, as well as enforce project standards.  There are many possibilities:

1. Generate warnings about syntax errors in your SQL files
2. Enforce system-wide naming conventions on column names
3. Verify that all foreign key columns actually have foreign key constraints
4. Set rules to determine what column types should/should not be used
5. ... more when I think of it

Mainly though, my intention is to make a linting system that is fully configurable by the end user.

**3. Better foreign key errors**

Does this look familiar?

```ERROR 1215 (HY000): Cannot add foreign key constraint```

I've seen developers at all skill levels waste many hours while creating foreign key constraints due to the above error from MySQL, which gives absolutely no hints as to what the problem actually is.  Because `mygrations` understands what the database is supposed to look like, it can detect the actual conditions that cause this error and provide a specific and actionable error message to the developer.

**4. Migration plans**

Again, because `mygrations` operates with knowledge of both the current database and the target database, it can present an actual migration plan before making any changes.  This makes it easy for the developer to have one last spot check before making changes, if desired.

**5. One table, one file**

Standard migration systems dedicate a file to each change of a database table.  As a result, it is very difficult to figure out what the database structure *should* be simply by looking at the contents of the migration directory.  Having one table per file makes it easy to spot check your migrations and make sure nothing has been missed.

**6. No Migration table**

Since `mygrations` works directly with the database structure it doesn't need to keep a history of which migrations it has run.  Instead, it brings your database up-to-spec no matter what state it is in: no more hassle if your migration table somehow gets out of sync with your migration files.

**7. Automatic migration builder**

Since the migration files are just simple `CREATE TABLE` commands, `mygrations` can create the migration files for you from your database.  Although you probably won't have to do that very often because the migrations files are very easy to build anyway.  A simple `SHOW CREATE TABLE` command from MySQL is all you need.

## Roadmap to 1.0

This is a brand new venture that is a long way from complete.  To give some guidance, here is my target feature list for when version 1.0 will officially be released:

1. Parsing of `CREATE TABLE` and `INSERT` commands and using those as migration definitions (Done)
2. Automatic foreign key dependency calculation (Sidelined)
3. Detailed foreign key error notices (Done)
4. Ability to migrate database to match definitions from any state (Done)
5. Generation of migration commands (Done)
6. Generation of migration files (Done)

Currently the system has reached a complete enough state that it is being tested in our real-world systems.
