https://dev.mysql.com/doc/refman/8.0/en/data-types.html

I'm moving a lot of functionality to core.definitions
I want to fill out core.definitions.columns.*
I want to move tests to exist in the same directory as their file -> test_filename.py
Also convert to proper Pep8 class names
Also add types
Parsers will then be invoked differently: parser(something).parse() will return a definition.database, instead of the weird thing returned now
The column parser will have to convert itself to the appropriate core.definition.columns.[class]
Also, note parsers are based on how the string "looks", so a single column parser may match both numeric and string columns
Moar tests!
