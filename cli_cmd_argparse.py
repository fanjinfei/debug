#!/usr/bin/env python

import argparse
import tempfile, sys
import code, traceback, signal, pdb
import readline
import cmd as ocmd

class Cmd(ocmd.Cmd):
    def emptyline(self):
        pass

def debug(sig, frame):
    """Interrupt running process, and provide a python prompt for
    interactive debugging."""
    d={'_frame':frame}         # Allow access to frame object.
    d.update(frame.f_globals)  # Unless shadowed by global
    d.update(frame.f_locals)

    i = code.InteractiveConsole(d)
    message  = "Signal received : entering python shell.\nTraceback:\n"
    message += ''.join(traceback.format_stack(frame))
    print(message)
    #i.interact(message)
    #pdb.set_trace()

def listen():
    sys.stdin = open('/dev/tty', 'r')
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

class SubInterpreter(Cmd):
    prompt = "(level2) "

    def do_subcommand_1(self, args):
        pass

    def do_subcommand_2(self, args):
        pass

    def do_quit(self, args):
        pass
        print("exit")
        return True
    do_EOF = do_quit

class MyInterpreter(Cmd):
    prompt = "(#) "
    def emptyline(self):
        pass
    def __init__(self, animals):
        Cmd.__init__(self)

        self.animals = animals

    def do_add(self, animal):
        print("Animal {0:s} added".format(animal))

    def completedefault(self, text, line, begidx, endidx):
        tokens = line.split()
        if tokens[0].strip() == "add":
            return self.animal_matches(text)
        return []

    def animal_matches(self, text):
        matches = []
        n = len(text)
        for word in self.animals:
            if word[:n] == text:
                matches.append(word)
        return matches


    def do_level1(self, args):
        pass

    def do_level2(self, args):
        sub_cmd = SubInterpreter()
        sub_cmd.cmdloop()
        print('done.')

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
animals = ["Bear", "Cat", "Cheetah", "Lion", "Zebra"]
mi = MyInterpreter(animals)
mi.cmdloop()
