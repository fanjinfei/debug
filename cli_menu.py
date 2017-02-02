#!/usr/bin/env python

import argparse, argcomplete
import sys

'''
#Example:

parser = argparse.ArgumentParser()
parser.add_argument('-g', '--global')
subparsers = parser.add_subparsers(dest="subparser_name") # this line changed
foo_parser = subparsers.add_parser('foo')
foo_parser.add_argument('-c', '--count')
bar_parser = subparsers.add_parser('bar')
args = parser.parse_args(['-g', 'xyz', 'foo', '--count', '42'])
print(args)

argcomplete.autocomplete(parser)
args = parser.parse_args()
print(args)
'''

'''
pip install argcomplete
activate-global-python-argcomplete --user
add source ~/.bash_completion.d/python-argcomplete.sh to .bashrc
add `eval "$(register-python-argcomplete your_script)"` to .bashrc
restart a shell
'''
class GroupedAction(argparse.Action):    
    def __call__(self, parser, namespace, values, option_string=None):
        group,dest = self.dest.split('.',2)
        groupspace = getattr(namespace, group, argparse.Namespace())
        setattr(groupspace, dest, values)
        setattr(namespace, group, groupspace)
# Main parser
main_parser = argparse.ArgumentParser()
main_parser.add_argument("-common")

filter_parser = argparse.ArgumentParser(add_help=False)
filter_parser.add_argument("--filter1", action=GroupedAction, dest='filter.filter1', default=argparse.SUPPRESS)
filter_parser.add_argument("--filter2", action=GroupedAction, dest='filter.filter2', default=argparse.SUPPRESS)

subparsers = main_parser.add_subparsers(help='sub-command help')

parser_a = subparsers.add_parser('command_a', help="command_a help", parents=[filter_parser])
parser_a.add_argument("--foo")
parser_a.add_argument("--bar")
parser_a.add_argument("--bazers", action=GroupedAction, dest='anotherGroup.bazers', default=argparse.SUPPRESS)
namespace = main_parser.parse_args()
print namespace

class FakeGit(object):

    def __init__(self):
        parser = argparse.ArgumentParser(
            description='Pretends to be git',
            usage='''git <command> [<args>]

The most commonly used git commands are:
   commit     Record changes to the repository
   fetch      Download objects and refs from another repository
''')
        parser.add_argument('command', help='Subcommand to run')
        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print 'Unrecognized command'
            parser.print_help()
            exit(1)
        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)()

    def commit(self):
        parser = argparse.ArgumentParser(
            description='Record changes to the repository')
        # prefixing the argument with -- means it's optional
        parser.add_argument('--amend', action='store_true')
        # now that we're inside a subcommand, ignore the first
        # TWO argvs, ie the command (git) and the subcommand (commit)
        args = parser.parse_args(sys.argv[2:])
        print 'Running git commit, amend=%s' % args.amend

    def fetch(self):
        parser = argparse.ArgumentParser(
            description='Download objects and refs from another repository')
        # NOT prefixing the argument with -- means it's not optional
        parser.add_argument('repository')
        args = parser.parse_args(sys.argv[2:])
        print 'Running git fetch, repository=%s' % args.repository


if __name__ == '__main__':
    #FakeGit()
    pass
