# -*- coding: utf-8 -*-
#



__author__ = "Epsirom"


class BaseError(Exception):

    def __init__(self, code, msg):
        super(BaseError, self).__init__(msg)
        self.code = code
        self.msg = msg

    def __repr__(self):
        return '[ERRCODE=%d] %s' % (self.code, self.msg)


class InputError(BaseError):

    def __init__(self, msg):
        super(InputError, self).__init__(1, msg)


class LogicError(BaseError):

    def __init__(self, msg):
        super(LogicError, self).__init__(2, msg)


class ValidateError(BaseError):

    def __init__(self, msg):
        super(ValidateError, self).__init__(3, msg)


class MySQLError(BaseError):

    def __init__(self, msg):
        super(MySQLError, self).__init__(4, msg)


class FileError(BaseError):

    def __init__(self, msg):
        super(FileError, self).__init__(5, msg)


class MenuError(BaseError):
    def __init__(self, msg):
        super(MenuError, self).__init__(6, msg)


class LogicError1(BaseError):
    def __init__(self, msg):
        super(LogicError, self).__init__(101, msg)


class LogicError2(BaseError):
    def __init__(self, msg):
        super(LogicError, self).__init__(102, msg)


class LogicError3(BaseError):
    def __init__(self, msg):
        super(LogicError, self).__init__(103, msg)


class LogicError4(BaseError):
    def __init__(self, msg):
        super(LogicError, self).__init__(104, msg)


class LogicError5(BaseError):
    def __init__(self, msg):
        super(LogicError, self).__init__(105, msg)


class LogicError6(BaseError):
    def __init__(self, msg):
        super(LogicError, self).__init__(106, msg)


class LogicError7(BaseError):
    def __init__(self, msg):
        super(LogicError, self).__init__(107, msg)


class LogicError8(BaseError):
    def __init__(self, msg):
        super(LogicError, self).__init__(108, msg)


class LogicError9(BaseError):
    def __init__(self, msg):
        super(LogicError, self).__init__(109, msg)