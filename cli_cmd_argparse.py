#!/usr/bin/env python

import cmd, argparse
import tempfile
import code, traceback, signal

def debug(sig, frame):
    """Interrupt running process, and provide a python prompt for
    interactive debugging."""
    d={'_frame':frame}         # Allow access to frame object.
    d.update(frame.f_globals)  # Unless shadowed by global
    d.update(frame.f_locals)

    i = code.InteractiveConsole(d)
    message  = "Signal received : entering python shell.\nTraceback:\n"
    message += ''.join(traceback.format_stack(frame))
    #i.interact(message)
    print(message)

def listen():
    signal.signal(signal.SIGUSR1, debug)  # Register handler

class WrapperCmdLineArgParser:
    def __init__(self, parser):
        """Init decorator with an argparse parser to be used in parsing cmd-line options"""
        self.parser = parser
        self.help_msg = ""

    def __call__(self, f):
        """Decorate 'f' to parse 'line' and pass options to decorated function"""
        if not self.parser:  # If no parser was passed to the decorator, get it from 'f'
            self.parser = f(None, None, None, True)

        def wrapped_f(*args):
            line = args[1].split()
            try:
                parsed = self.parser.parse_args(line)
            except SystemExit:
                return
            f(*args, parsed=parsed)

        wrapped_f.__doc__ = self.__get_help(self.parser)
        return wrapped_f

    @staticmethod
    def __get_help(parser):
        """Get and return help message from 'parser.print_help()'"""
        f = tempfile.SpooledTemporaryFile(max_size=2048)
        parser.print_help(file=f)
        f.seek(0)
        return f.read().rstrip()

class SubInterpreter(cmd.Cmd):
    prompt = "(level2) "

    def do_subcommand_1(self, args):
        pass

    def do_subcommand_2(self, args):
        pass

    def do_quit(self, args):
        return True
    do_EOF = do_quit

class MyInterpreter(cmd.Cmd):
    def do_level1(self, args):
        pass

    def do_level2(self, args):
        sub_cmd = SubInterpreter()
        sub_cmd.cmdloop()

    def do_level3(self, args):
        pass
    #static attributes
    __test1_parser = argparse.ArgumentParser(prog="test1")
    __test1_parser.add_argument('--foo', help="foo help")

    @WrapperCmdLineArgParser(parser=__test1_parser)
    def do_test1(self, line, parsed):
        print("Test1...")
        print(parsed)

    @WrapperCmdLineArgParser(parser=None)
    def do_test2(self, line, parsed, get_parser=False):
        if get_parser:
            parser = argparse.ArgumentParser(prog="test2")
            parser.add_argument('--bar', help="bar help")
            return parser

        print("Test2...")
        print(parsed)
    def do_quit(self, args):
        return True
    do_EOF = do_quit
listen()
mi = MyInterpreter()
mi.cmdloop()
