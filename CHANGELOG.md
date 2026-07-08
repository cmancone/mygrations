# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Add automation
- Add support for if not exists on create table

### Changed
- Add auto-created indexes for bare FOREIGN KEY constraints
- Fix MySQL DDL parser for standard syntax and modernize tests
- Use modern tools

### Fixed
- Pre-existing copy-paste bug in table.py _find_all_errors
- Fix: include source table name in auto-generated FK constraint names
- Fix: resolve charset/collate false errors on INTEGER and BOOLEAN columns

## [1.0.7] - 2023-08-12

### Added
- Added version command and made it default
- Added public methods to table to modify, tests coming next
- Adding some notes for later
- Added 'add_table' to database by @cmancone
- Added section for dependencies
- Adding in convert-to-string on columns: not done adding tests yet by @cmancone
- Adding tests for mysql parsers, small bug fixes by @cmancone
- Added doc blocks and unit tests for parse_delimited by @cmancone

### Changed
- Minor bug fix by @cmancone
- More flexibility for some DBs by @cmancone
- Datetime defaults by @cmancone
- Return success status for runner by @cmancone
- Merge pull request #25 from cmancone/feature/reorg by @cmancone
- Minor updates to play nice with clearskies by @cmancone
- Merge pull request #24 from cmancone/feature/reorg by @cmancone
- Cleanup notes by @cmancone
- Setup pre-commit with YAPF by @cmancone
- Final changes by @cmancone
- Direct execution instructions by @cmancone
- Working on new calling sequence to support direct integrations by @cmancone
- Ditching concept of auto incrementing ids for row tracking by @cmancone
- Tweaks as I test in more detail by @cmancone
- Done with test reorg by @cmancone
- MOAR TESTSgit add .! by @cmancone
- Next round of tests by @cmancone
- Endless test restoration! by @cmancone
- Switch to pymysql, moar tests by @cmancone
- Moar tests! by @cmancone
- Pulling over integration tests by @cmancone
- Current tests pass! by @cmancone
- Working through test changes and bugs by @cmancone
- Another gigantic overhaul by @cmancone
- The reorg continues! by @cmancone
- Start on column definition reorg by @cmancone
- Tweak by @cmancone
- Streamline... by @cmancone
- Acronym not required by @cmancone
- Update README.me by @cmancone
- Merging mysql and core table definitions by @cmancone
- Finally, a better error validation flow! by @cmancone
- Splitting out errors and overhauling their collection by @cmancone
- Let yapf have its way by @cmancone
- Camel case classes by @cmancone
- Operations complete by @cmancone
- Working through operations updates and basic tests by @cmancone
- Working through classes operation classes by @cmancone
- Getting started on moving operations to core by @cmancone
- Check for issue #5 by @cmancone
- Starting tests on table by @cmancone
- Working on table overhaul and better organization for error checks by @cmancone
- Options by @cmancone
- Final touches on constraints and indexes by @cmancone
- Half ass date class by @cmancone
- Enum + tests by @cmancone
- Numeric tests by @cmancone
- Started on table but then moved over to error check overhaul by @cmancone
- Indexes by @cmancone
- Basic filler for date+enum and constraint by @cmancone
- Numeric and String by @cmancone
- Starting on new core columns and new test organization by @cmancone
- Starting a big overhaul by @cmancone
- Small format fix by @cmancone
- Updates to readme including link to example repo by @cmancone
- Missed some test breakage by @cmancone
- Bump version number
- Merge pull request #22 from cmancone/feature/pypi_markdown by @cmancone
- Small fix for pypi and markdown
- Merge pull request #21 from cmancone/feature/stderr_flexible_path by @cmancone
- Preemptive setup.py update
- Check parents for mygrate.conf file and make sure paths stay relative to it
- In the event of SQL errors send output to stderr instead of stdout
- Merge pull request #20 from cmancone/feature/execute by @cmancone
- Including the 'apply' command
- Merge pull request #19 from cmancone/development by @cmancone
- Merge pull request #18 from cmancone/feature/auto-format by @cmancone
- Auto formating code with yapf by @cmancone
- Merge branch 'master' of github.com:cmancone/mygrations by @cmancone
- Merge pull request #17 from cmancone/development by @cmancone
- Merge pull request #16 from cmancone/feature/travis-ci by @cmancone
- Attempting to adjust script location by @cmancone
- Trying a pip3 install for dependency by @cmancone
- Working on dependencies for ci by @cmancone
- First test with travis-ci by @cmancone
- Merge branch 'master' into development by @cmancone
- Merge pull request #11 from cmancone/feature/INDEX by @cmancone
- [2] support for INDEX keyword + tests
- Merge branch 'mysql' into development
- Merge branch 'development' into mysql
- Merge branch 'master' into development
- Merge branch 'development' into mysql
- Merge branch 'development' into mysql
- Travis icon by @cmancone
- Merge pull request #15 from dhananjay1995/patch-1 by @cmancone
- Minor change by @dhananjay-ranium
- Merge branch 'development'
- Merge branch 'master' into development
- Couple small changes
- Merge branch 'mysql' into development
- Proper null handling + tests
- Straightening out some test names
- Cleanup! by @cmancone
- Double backslashes on update by @cmancone
- Starting to straighten out quotes by @cmancone
- Merge branch 'development' into mysql
- Version
- Update README.md by @cmancone
- Ready for 0.9.3
- Sigh...
- Version update
- Wrong package ref
- Some cleanup for packaging
- Merge branch 'development'
- Made mygrate.py execution more environment-dependent
- Readme update
- Merge
- Nice output for command line usage
- Exports!
- Small bug fix and adjusting plan command
- Enabled loose type checking
- Adjustment so that disable FK happens for alters and row updates
- Floats were working but threw in a test anyway
- No more false positives caused by decimal defaults
- Hide full plan in event of error
- Missed a 1215 error condition + test
- Fix + tests for mysql causing false positives
- Including row migrations in migration plan command
- Split drop foreign keys off to their own operation + tests
- First test on row migration
- I always forget the semi-colons...
- Ready for first round of testing on row migration by @cmancone
- Accounting for escaping on input by @cmancone
- Row operations! by @cmancone
- //xkcd.com/1296/
- One more try
- Quick tweaks so I can start testing in our system
- Finished reading rows for live database objects + test
- Removing extraneous file
- Getting ready for row reading by @cmancone
- Finally split mysql connection out to its own wrapper class by @cmancone
- Getting started on row syncs by @cmancone
- Some little tweaks while preparing for the next big phase by @cmancone
- Typo got missed somehow by @cmancone
- Was missing the semi-colon on the end of  + tests
- Forgot to strip backticks from insert table name + regression test
- Command base + second command + new default
- Bug fix + regression tests
- First changes based on real usage
- Missed guard for simple condition
- Forgot a param
- Typo fix
- Runner update to allow for selecting only some of the tests
- Forgot one
- Tests fully adjusted for new process loop
- New mygration flow, in the middle of adjusting tests by @cmancone
- ... by @cmancone
- 1215 errors are now checked separately (and first) during mygration + tests by @cmancone
- Sigh by @cmancone
- Last tests on column_is_indexed by @cmancone
- Some small adjustments by @cmancone
- Updated docstring summary for class
- Basic test coverage for the primary processing loop.  Should probably try to come up with some good edge cases
- More tests: forgot that I need to add  to all my ops by @cmancone
- Small bug fix and first tests on resolving FKs for mygration: Success! by @cmancone
- Tests for key operations, couple more column tests and exceptions
- Table operations + first tests
- One more test for remove_table
- Theoretically we are now migrating!  Need to start testing
- Got a serious game plan now
- Slight adjustment to split_operations return again + test
- Forgot a 1215 error condition + test
- Adjusted what 'split_results' does for table.to + test
- Nothing to add here by @cmancone
- More slow progress: lots to think through by @cmancone
- Making progress... by @cmancone
- Changed name and return value of definitions.database.fulfills_fks by @cmancone
- More tests for Foreign key resolution by @cmancone
- Very first mygration step and test by @cmancone
- Properly determines if FK can be fulfilledd, explains 1215 errors + tests by @cmancone
- Table comparisons getting started by @cmancone
- Tables can now return a create table operation or convert directly into a string by @cmancone
- Forgot to print out AUTO_INCREMENT when set by @cmancone
- Some more tests and small bug fixes for table differences by @cmancone
- First functional results and tests on table difference
- First run for alter table: working through tests and bugs by @cmancone
- More progress towards individual table migrations
- Stringificiaton for FKs and slowly piecing together the operations by @cmancone
- Conversion to string for indexes
- Tests for to string conversion on all field types
- Getting organized for migration calculations! by @cmancone
- Small bug fix: was turning the comma in a decimal length into a period by @cmancone
- Getting moving with database comparisons by @cmancone
- Mock and tests for MySQL database reader by @cmancone
- First steps in database reading by @cmancone
- Some more tests for table and database
- First test for database rows
- Working on row ingestion for tables by @cmancone
- Database is now properly factored out as a definition by @cmancone
- Decided to have comment errors work the same as everyone else by @cmancone
- Made sure all warnings make their way up to the database by @cmancone
- Moved errors and warnings into definitions by @cmancone
- Ignore kate temporary files by @cmancone
- Working towards database by @cmancone
- Moving to 'database' reading by @cmancone
- Some tests on inserts, also definition class for rows container by @cmancone
- Finished indexes and added table definition by @cmancone
- Refactor on indexes by @cmancone
- Moving to inheritence-driven contracts by @cmancone
- Creating base classes by @cmancone
- Forgot to strip backticks by @cmancone
- Getting organized! by @cmancone
- Getting ready for next steps by @cmancone
- Tests for text type.  All done! by @cmancone
- Tests for type plain by @cmancone
- Tests for numeric type: almost done! by @cmancone
- Tests for enum by @cmancone
- Tests for decimal type by @cmancone
- Small adjustments by @cmancone
- Tests for type_character plus small bug fixes by @cmancone
- Continuing to test mysql parsers by @cmancone
- Small bug fixes and first tests for mysql parsers by @cmancone
- Finished adding processing rules
- Parser processing by @cmancone
- More tests for parse_children by @cmancone
- Small bug fixes and tests for rule_children by @cmancone
- Test for newly refactored literal rule by @cmancone
- Test for newly refactored regex rule by @cmancone
- Refactored core.parser.parser to separate out rules: should have done that from the start by @cmancone
- Parsing of CREATE TABLE and INSERT queries! (basics anyway) by @cmancone
- README update: project goals by @cmancone
- First step to MySQL parsing by @cmancone
- Merge branch 'master' into development
- Fix some typos
- README update: project goals by @cmancone
- Setting up configuration management by @cmancone
- Rough project organization, executor, and headed to import_files by @cmancone
- Allow semi-colon at end of line by @cmancone
- Dotenv parsing and associated tests by @cmancone
- Initial commit by @cmancone

### Fixed
- Tests on row mygration + bug fixes
- Tests for constraint operations

### Removed
- Remove FKs first + test adjustment
- Remove table from database + test

## New Contributors
* @cmancone made their first contribution
* @ made their first contribution
* @dhananjay-ranium made their first contribution
[unreleased]: https://github.com/tnijboer/mygrations/compare/1.0.7..HEAD

<!-- generated by git-cliff -->
