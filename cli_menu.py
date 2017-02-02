#!/usr/bin/env python
import argparse, argcomplete
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
pip install argcomplete
activate-global-python-argcomplete --user
add source ~/.bash_completion.d/python-argcomplete.sh to .bashrc
add `eval "$(register-python-argcomplete your_script)"` to .bashrc
restart a shell
'''
