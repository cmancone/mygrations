__ver__ = '1.0'

import io
import os
import re

import json
from json import JSONDecodeError
class DotEnvSyntaxError(Exception):
    pass
class dotenv(dict):

    raw_contents = ''
    comment = ''
    comment_length = 0

    def __init__(self, filename='', comment='#'):

        # we are going to allow a few different values for filename.
        # we will allow an actual string to parse, a string as a filename,
        # a file object, or an IO stream.  get_contents will handle the
        # details
        if filename:
            self.raw_contents = self.get_contents(filename)

            # and parse
            parsed = self.parse(self.raw_contents, comment)

        else:
            self.raw_contents = ''
            parsed = {}

        super().__init__(parsed)

    def get_contents(self, filename):

        # file pointer
        if isinstance(filename, io.IOBase):
            contents = filename.read()

        # and an actual string
        elif isinstance(filename, str):

            # which could be a filename
            if os.path.isfile(filename):
                fp = open(filename, 'r')
                contents = fp.read()
                fp.close()
            else:
                contents = filename

        else:
            raise ValueError(
                "Unknown type for filename: must be an ascii string, a filename, file pointer, or StringIO"
            )

        # we didn't end up with bytes, did we?
        try:
            contents = contents.decode()
        except AttributeError:
            pass

        return contents

    def parse(self, string, comment='#'):

        # this isn't json, is it?
        parsed = False
        try:
            parsed = json.loads(string)
        except JSONDecodeError:
            pass

        # because if it is, this is very easy
        if parsed:
            return parsed

        # This will hold our results
        configs = {}

        # okay then!  Let's get started.  Divide up by newlines and work from there
        for line in string.split("\n"):

            # we're not actually going to do much here
            [key, value] = self.parse_line(line, comment)

            # we will get a non-value for key and value if this wasn't
            # a valid data line
            if not key or not value:
                continue

            # store it!
            configs[key] = value

        # that's it
        return configs

    def parse_line(self, line, comment):

        # clean it
        clean = line.strip()

        # see if we start with a comment character
        if clean[:len(comment)] == comment:
            return [False, False]

        # also ignore empty lines
        if not clean:
            return [False, False]

        # we want to do actual parsing, instead of doing
        # it the easy way and just splitting on an equal sign.
        # this is mainly intended to give some flexibility to support
        # a few different potentially common formats.  For instance,
        # an equal sign is a common delimiter between key and value,
        # but a colon (for a JSON-like syntax) may also be used.
        match = re.match('^([^=:]+)[=:](.*)', clean)

        # if that didn't match anything then we don't have a config
        if not match:
            raise DotEnvSyntaxError("Syntax error: no data found in line: %s" % line)

        # otherwise we will continue on our way.  Clean everything up.
        key = match.group(1).strip()
        value = match.group(2).strip()

        # non-value?
        if not value:
            return [key, '']

        # our key should be good to go.  Our value needs some checking.
        # it may be surrounded by quotes (single or double).  It may
        # have a comment character at the end, or it may have a comment
        # character inside a quoted string which is not actually a comment.
        # therefore, we need some fancy parsing.

        # the main starting question is whether or not our value starts
        # with a quote.  If not this is easy.
        if value[0] != "'" and value[0] != '"':

            # just check for a comment
            # and remove it if found
            if value.count(comment):
                value = value[:value.index(comment)].strip()

            # if we have a quote character elsewhere in the value though,
            # we have a problem
            if value.count('"') or value.count("'"):
                raise DotEnvSyntaxError("Syntax error: unclosed quote in line %s" % line)

            return [key, value]

        # if we got here then we have a quoted string.  We want to validate the syntax,
        # remove the quotes, check for escaped quotes, and check for comment
        quote = value[0]
        value = value[1:]

        # syntax error?
        if not value.count(quote):
            raise DotEnvSyntaxError("Syntax error: unclosed quote in line %s" % line)

        # do we have an empty string?
        if value[0] == quote:
            return [key, '']

        # make sure we don't have an escaped quote in our quoted string
        index = 0
        while value.count(quote, index):
            index = value.index(quote, index + 1)
            if value[index - 1] == '\\':
                continue

            # if we get here then we have found the ending quote!

            # check for a comment
            if value.count(comment, index):
                value = value[:value.index(comment, index)].strip()

            # our string should end at the closing quote, although safely ignore a closing semi-colon
            if len(value) > index + 1 and value[index + 1:].strip() != ';':
                raise DotEnvSyntaxError("Syntax error: data found outside of the quote in line %s" % line)

            # don't forget to unescape any quotes and return
            return [key, value[:index].replace('\\%s' % quote, quote)]

        # if we got here then we didn't find anything
        raise DotEnvSyntaxError("Syntax error: unclosed quote in line %s" % line)
