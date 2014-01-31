import os

from pulsar import Setting

import lux


class Command(lux.Command):
    option_list = (
        Setting('plain', ('-p', '--plain'),
                action='store_true',
                default=False,
                desc='Use plain Python shell, not IPython.'),
    )
    help = "Runs a Python interactive interpreter. Use IPython if available"
    shells = ['ipython', 'bpython']

    def ipython(self):  # pragma nocoverage
        try:
            from IPython.frontend.terminal.embed import (
                TerminalInteractiveShell)
            shell = TerminalInteractiveShell()
            shell.mainloop()
        except ImportError:
            # IPython < 0.11
            # Explicitly pass an empty list as arguments, because otherwise
            # IPython would use sys.argv from this script.
            try:
                from IPython.Shell import IPShell
                shell = IPShell(argv=[])
                shell.mainloop()
            except ImportError:
                # IPython not found at all, raise ImportError
                raise

    def bpython(self):   # pragma    nocover
        import bpython
        bpython.embed()

    def run_shell(self):     # pragma    nocover
        for shell in self.shells:
            try:
                return getattr(self, shell)()
            except ImportError:
                pass
        raise ImportError

    def run(self, argv, **params):     # pragma    nocover
        options = self.options(argv)
        use_plain = options.plain
        try:
            if use_plain:
                raise ImportError()
            self.run_shell()
        except ImportError:
            import code
            # Set up a dictionary to serve as the environment for the shell,
            # so that tab completion works on objects that are imported at
            # runtime.
            imported_objects = {}
            try:  # Try activating rlcompleter, because it's handy.
                import readline
            except ImportError:
                pass
            else:
                # We don't have to wrap the following import in a 'try',
                # because we already know 'readline' was imported successfully.
                import rlcompleter
                readline.set_completer(
                    rlcompleter.Completer(imported_objects).complete)
                readline.parse_and_bind("tab:complete")

            # We want to honor both $PYTHONSTARTUP and .pythonrc.py,
            # so follow system
            # conventions and get $PYTHONSTARTUP first then import user.
            if not use_plain:
                pythonrc = os.environ.get("PYTHONSTARTUP")
                if pythonrc and os.path.isfile(pythonrc):
                    try:
                        execfile(pythonrc)
                    except NameError:
                        pass
                # This will import .pythonrc.py as a side-effect
                import user
            code.interact(local=imported_objects)
