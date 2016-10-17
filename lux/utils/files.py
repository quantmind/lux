'''
Some code is taken from django:

    Copyright (c) Django Software Foundation and individual contributors.
    All rights reserved.
'''
import os
import re
import itertools


__all__ = ['Filehandler']


def skipfile(name):
    return name.startswith('.') or name.startswith('_')


def directory(dir):
    bd, fname = os.path.split(dir)
    return dir if fname else bd


def get_rel_dir(dir, base, res=''):
    '''Return the ``base`` path relative to ``dir``
    '''
    dir = directory(dir)
    base = directory(base)
    if len(base) > len(dir):
        raise RuntimeError('Base directory not in path')
    if dir == base:
        return res
    dir, fname = os.path.split(dir)
    if res:
        fname = os.path.join(fname, res)
    return get_rel_dir(dir, base, fname)


def get_valid_filename(s):
    """
    Returns the given string converted to a string that can be used for a clean
    filename. Specifically, leading and trailing spaces are removed; other
    spaces are converted to underscores; and anything that is not a unicode
    alphanumeric, dash, underscore, or dot, is removed.
    >>> get_valid_filename("john's portrait in 2004.jpg")
    'johns_portrait_in_2004.jpg'
    """
    s = s.strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)


class Filehandler:

    def open(self, name, mode='rb'):
        """Retrieves the specified file from storage, using the optional mixin
        class to customize what features are available on the File returned.
        """
        raise NotImplementedError()

    def save(self, file):
        '''Save an instance of :class:`~.File` into the backened storage.'''
        name = file.name
        name = self.get_available_name(name)
        name = self._save(name, file)
        # Store filenames with forward slashes, even on Windows
        return name.replace('\\', '/')

    # These methods are part of the public API, with default implementations.

    def get_valid_name(self, name):
        """
        Returns a filename, based on the provided filename, that's suitable for
        use in the target storage system.
        """
        return get_valid_filename(name)

    def get_available_name(self, name):
        """
        Returns a filename that's free on the target storage system, and
        available for new content to be written to.
        """
        dir_name, file_name = os.path.split(name)
        file_root, file_ext = os.path.splitext(file_name)
        # If the filename already exists, add an underscore and a number
        # (before the file extension, if one exists) to the filename until
        # the generated filename doesn't exist.
        count = itertools.count(1)
        while self.exists(name):
            # file_ext includes the dot.
            name = os.path.join(dir_name, "%s_%s%s" %
                                (file_root, next(count), file_ext))

        return name

    def path(self, name):
        """
        Returns a local filesystem path where the file can be retrieved using
        Python's built-in open() function. Storage systems that can't be
        accessed using open() should *not* implement this method.
        """
        raise NotImplementedError(
            "This backend doesn't support absolute paths.")

    # The following methods form the public API for storage systems, but with
    # no default implementations. Subclasses must implement *all* of these.

    def delete(self, name):
        """
        Deletes the specified file from the storage system.
        """
        raise NotImplementedError()

    def exists(self, name):
        """
        Returns True if a file referened by the given name already exists
        in the storage system, or False if the name is available for a
        new file.
        """
        raise NotImplementedError()

    def listdir(self, path):
        """
        Lists the contents of the specified path, returning a 2-tuple of lists;
        the first item being directories, the second item being files.
        """
        raise NotImplementedError()

    def size(self, name):
        """
        Returns the total size, in bytes, of the file specified by name.
        """
        raise NotImplementedError()

    def url(self, name):
        """
        Returns an absolute URL where the file's contents can be accessed
        directly by a Web browser.
        """
        raise NotImplementedError()

    def accessed_time(self, name):
        """
        Returns the last accessed time (as datetime object) of the file
        specified by name.
        """
        raise NotImplementedError()

    def created_time(self, name):
        """
        Returns the creation time (as datetime object) of the file
        specified by name.
        """
        raise NotImplementedError()

    def modified_time(self, name):
        """
        Returns the last modified time (as datetime object) of the file
        specified by name.
        """
        raise NotImplementedError()
