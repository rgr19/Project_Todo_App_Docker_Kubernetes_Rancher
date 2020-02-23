#!/usr/bin/env python3

import logging
from typing import Type

from logutils.colorize import ColorizingStreamHandler
import abc


class FileHandler(logging.FileHandler):
    """ A base logging handler optimized for terminal debugging aestetichs.

    - Designed for diagnosis and debug mode output - not for disk logs

    - Highlight the content of logging message in more readable manner

    - Show function and line, so you can trace where your logging messages
      are coming from

    - Keep timestamp compact

    - Extra module/function output for traceability

    The class provide few options as member variables you
    would might want to customize after instiating the handler.
    """
    #: How many characters reserve to function name logging
    who_padding = 22

    #: Show logger name
    show_name = True

    def parse_who(self, record):
        who = [getattr(record, "funcName", ""),
               "()",
               ":",
               str(getattr(record, "lineno", 0))]

        who = "".join(who)

        # We need to calculate padding length manualy
        # as color codes mess up string length based calcs
        unformatted_who = getattr(record, "funcName", "") + "()" + \
                          ":" + str(getattr(record, "lineno", 0))

        if len(unformatted_who) < self.who_padding:
            spaces = " " * (self.who_padding - len(unformatted_who))
        else:
            spaces = ""

        record.padded_who = who + spaces

    def parse_format(self, record):

        template = [
            "[",
            "%(asctime)s",
            "] [",
            "%(name)s" if self.show_name else "",
            ".",
            "%(padded_who)s",
            "] MSG: { ",
            "%(message)s",
            " }",
        ]

        format = "".join(template)

        formatter = logging.Formatter(format, )
        self.parse_traceback(formatter, record)
        output = formatter.format(record)
        # Clean cache so the color codes of traceback don't leak to other formatters
        record.ext_text = None
        return output

    def parse_traceback(self, formatter, record):
        """
        Turn traceback text to red.
        """

        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            record.exc_text = "".join([
                formatter.formatException(record.exc_info),
            ])

    def format(self, record):
        """
        Formats a record for output.

        Takes a custom formatting path on a terminal.
        """
        message = type(super()).format(self, record)

        return message



