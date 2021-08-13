#!/usr/bin/python
# -*- coding: utf8


class SQLGenException(Exception):
    pass


class KeyAlreadyExists(KeyError):
    pass


class InValidReservedWords(SQLGenException):
    pass


class InValidTemplate(SQLGenException):
    pass
