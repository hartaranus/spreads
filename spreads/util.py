# -*- coding: utf-8 -*-

# Copyright (c) 2013 Johannes Baiter. All rights reserved.
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

""" Various utility functions.
"""

from __future__ import division, unicode_literals

import abc
import itertools
import logging
import os
import platform

import blinker
import psutil
from colorama import Fore, Back, Style
from spreads.vendor.pathlib import Path


class SpreadsException(Exception):
    pass


class DeviceException(SpreadsException):
    pass


class MissingDependencyException(SpreadsException):
    pass


def find_in_path(name):
    """ Find executable in $PATH.

    :param name:  name of the executable
    :type name:   unicode
    :returns:     bool -- True if *name* is found or False

    """
    candidates = None
    if platform.system() == "Windows":
        import winreg
        if name == 'scantailor':
            try:
                cmd = winreg.QueryValue(
                    winreg.HKEY_CLASSES_ROOT,
                    'Scan Tailor Project\\shell\\open\\command')
                return cmd.split('" "')[0][1:]
            except OSError:
                return None
        else:
            path_dirs = os.environ.get('PATH').split(';')
            path_dirs.append(os.getcwd())
            path_exts = os.environ.get('PATHEXT').split(';')
            candidates = (os.path.join(p, name + e)
                          for p in path_dirs
                          for e in path_exts)
    else:
        candidates = (os.path.join(p, name)
                      for p in os.environ.get('PATH').split(':'))
    try:
        return next(c for c in candidates if os.path.exists(c))
    except StopIteration:
        return None


def check_futures_exceptions(futures):
    if any(x.exception() for x in futures):
        exc = next(x for x in futures if x.exception()).exception()
        raise exc


def get_free_space(path):
    return psutil.disk_usage(unicode(path)).free


class _instancemethodwrapper(object):
    def __init__(self, callable):
        self.callable = callable
        self.__dontcall__ = False

    def __getattr__(self, key):
        return getattr(self.callable, key)

    def __call__(self, *args, **kwargs):
        if self.__dontcall__:
            raise TypeError('Attempted to call abstract method.')
        return self.callable(*args, **kwargs)


class _classmethod(classmethod):
    def __init__(self, func):
        super(_classmethod, self).__init__(func)
        isabstractmethod = getattr(func, '__isabstractmethod__', False)
        if isabstractmethod:
            self.__isabstractmethod__ = isabstractmethod

    def __get__(self, instance, owner):
        result = _instancemethodwrapper(super(_classmethod, self)
                                        .__get__(instance, owner))
        isabstractmethod = getattr(self, '__isabstractmethod__', False)
        if isabstractmethod:
            result.__isabstractmethod__ = isabstractmethod
            abstractmethods = getattr(owner, '__abstractmethods__', None)
            if abstractmethods and result.__name__ in abstractmethods:
                result.__dontcall__ = True
        return result


class abstractclassmethod(_classmethod):
    """ New decorator class that implements the @abstractclassmethod decorator
        added in Python 3.3 for Python 2.7.

        Kudos to http://stackoverflow.com/a/13640018/487903

    """
    def __init__(self, func):
        func = abc.abstractmethod(func)
        super(abstractclassmethod, self).__init__(func)


class ColourStreamHandler(logging.StreamHandler):
    """ A colorized output StreamHandler
    Kudos to Leigh MacDonald:
    http://leigh.cudd.li/article/Cross_Platform_Colorized_Logger_Output_Using_Pythons_logging_Module_And_Colorama
    """

    # Some basic colour scheme defaults
    colours = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARN': Fore.YELLOW,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRIT': Back.RED + Fore.WHITE,
        'CRITICAL': Back.RED + Fore.WHITE
    }

    @property
    def is_tty(self):
        """ Check if we are using a "real" TTY. If we are not using a TTY it
        means that the colour output should be disabled.

        :return: Using a TTY status
        :rtype: bool
        """
        try:
            return getattr(self.stream, 'isatty', None)()
        except:
            return False

    def emit(self, record):
        try:
            message = self.format(record)
            if not self.is_tty:
                self.stream.write(message)
            else:
                self.stream.write(self.colours[record.levelname]
                                  + message + Style.RESET_ALL)
            self.stream.write(getattr(self, 'terminator', '\n'))
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


class EventHandler(logging.Handler):
    signals = blinker.Namespace()
    on_log_emit = signals.signal('logrecord', doc="""\
    Sent when a log record was emitted.

    :keyword :class:`logging.LogRecord` record: the LogRecord
    """)

    def emit(self, record):
        self.on_log_emit.send(record=record)


def get_data_dir(create=False):
    UNIX_DIR_VAR = 'XDG_DATA_DIRS'
    UNIX_DIR_FALLBACK = '~/.config'
    WINDOWS_DIR_VAR = 'APPDATA'
    WINDOWS_DIR_FALLBACK = '~\\AppData\\Roaming'
    MAC_DIR = '~/Library/Application Support'
    base_dir = None
    if platform.system() == 'Darwin':
        if Path(UNIX_DIR_FALLBACK).exists:
            base_dir = UNIX_DIR_FALLBACK
        else:
            base_dir = MAC_DIR
    elif platform.system() == 'Windows':
        if WINDOWS_DIR_VAR in os.environ:
            base_dir = os.environ[WINDOWS_DIR_VAR]
        else:
            base_dir = WINDOWS_DIR_FALLBACK
    else:
        if UNIX_DIR_VAR in os.environ:
            base_dir = os.environ[UNIX_DIR_VAR]
        else:
            base_dir = UNIX_DIR_FALLBACK
    app_path = Path(base_dir)/'spreads'
    if create and not app_path.exists():
        app_path.mkdir()
    return unicode(app_path)
