# mygrations

A general purpose migration tool for managing MySQL updates.  Written in python but intended for use in other sysetms as well, especially PHP.

## About

`mygrations` manages database migrations with a declarative approach.  Each table in your database has one SQL file which contains a `CREATE TABLE` command that gives the table definition.  This command isn't used directly to create your table.  Rather, it defines the table structure that `mygration` will create.  When it comes time to migrate your database, `mygrations` parses the SQL to determine the structure of the table you are trying to build.  It then compares this to the actual table structure in MySQl to determine all of the changes that need to happen to bring the database up to spec.  Finally, it generates and applies any necessary `ALTER TABLE` commands or creates the table if it doesn't exist.

When you need to change a table structure you don't generate additional migration files, but instead simply edit the `CREATE TABLE` command inside the original table definition file.  When migrating multiple tables related via foreign key constraints you simply have to define your foreign keys in the `CREATE TABLE` command normally.  `mygrations` will take note of the foreign keys and use them to determine the necessary order to build the tables in.
..
## Advantages

There are plenty of migration tools out there, and many frameworks come with their own.  So why would I write another, and why would anyone setup a new tool if one comes out-of-the-box with their framework of choice?  Because the declarative approach taken by `mygrations` has a number of concrete advantages.

**1. Database structure trackable by version control**

In `mygrations` each database is defined by a single `CREATE TABLE` command living in one file.  Adjusting a table's structure means adjusting the `CREATE TABLE` command in the table's definition file.  As a result, if two developers attempt to change the same table in conflicting ways, the conflict will be picked up immediately at merge time by your version control system.  Because normal migration systems put each database change in its own file (and because the changes are in code instead of written declaratively) version control cannot pick up any conflicts.  Instead, conflicting table definitions are not found until after a merge when the next migration is run and an SQL error is generated.  This way, potential conflicts are found much sooner.

**2. MySQL Linting**

Unlike normal migration systems which simply apply developer-provided transformations to update your tables, `mygrations` is an intelligent tool that understand the actual structure you are trying to create.  As a result it is possible to perform intelligent checks to find "errors" that might otherwise go unnoticed.  There are many possibilities:

1. Enforce system-wide naming conventions on column names
2. Verify that all foreign key columns actually have foreign key constraints
3. Set rules to determine what column types should/should not be used
4. ... more when I think of it

**3. Better foreign key errors**

Does this look familiar?

```ERROR 1215 (HY000): Cannot add foreign key constraint```

I've seen developers at all skill levels waste many errors while creating foreign key constraints due to the above error from MySQL, which gives absolutely no hints as to what the problem actually is.  Because `mygrations` understands what the database is supposed to look like, it can detect the actual conditions that cause this error and provide a meaningful error message to the developer.

**4. Migration plans**

Again, because `mygrations` operates with knowledge of both the current database and the target database, it can present an actual migration plan before making any changes.  This makes it easy for the developer to have one last spot check before making changes, if desired.

**5. One table, one file**

Standard migration systems dedicate a file to each change of a database table.  As a result, it is very difficult to figure out what the database structure *should* be simply by looking at the contents of the migration directory.  Having one table per file makes it easy to spot check your migrations and make sure nothing has been missed.

**6. No Migration table**

Since `mygrate` works intelligently with the database structure it doesn't need to keep a history of which migrations it has run so that it knows where to continue from.  Instead, it brings your database up-to-spec no matter what state it is in: no more hassle if your migration table somehow gets out of sync with your migration files.

**7. Automatic migration builder**

Since the migration files are just simple `CREATE TABLE` commands, `mygrations` can create the migration files for you from your database.  Although you probably won't have to do that very often because the migrations files are very easy to build anyway.  A simple `SHOW CREATE TABLE` command from MySQL is all you need.

## Roadmap to 1.0

This is a brand new venture that is a long way from complete (or even working).  To give some guidance, here is my target feature list for when version 1.0 will officially be released:

1. Parsing of `CREATE TABLE` and `INSERT` commands and using those as migration definitions
2. Automatic foreign key dependency calculation
3. Detailed foreign key error notices
4. Ability to migrate database to match definitions from any state
5. Generation of migration commands
6. Generation of migration files
