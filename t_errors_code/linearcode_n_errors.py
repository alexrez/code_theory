import argparse

import codemodes as cm
import func

parser = argparse.ArgumentParser(prog='linearcode', usage='%(prog)s mode param',
                                 description='Linear error-correcting code.')

subparsers = parser.add_subparsers(title='mode', description='valid modes', help='additional help')

parser_gencode = subparsers.add_parser('gencode', help='generating code')
parser_gencode.add_argument('r', type=int, help='number of check bits')
parser_gencode.add_argument('n', type=int, help='length of a code word')
parser_gencode.add_argument('t', type=int, help='number of error to correct')
parser_gencode.add_argument('--out-file', dest='out', type=str, default='code_information.pickle',
                            help='file whith information for coder/decpder (default: code_information.pickle)')
parser_gencode.set_defaults(func=cm.gencode)

parser_coder = subparsers.add_parser('coder', help='coder')
parser_coder.add_argument('inputfile', type=str, help='file whith information for coder')
parser_coder.add_argument('m', type=str, help='message')
parser_coder.add_argument('-e', dest='e', type=str, help='error', default=None)
parser_coder.set_defaults(func=cm.coder)

parser_decoder = subparsers.add_parser('decoder', help='decoder')
parser_decoder.add_argument('inputfile', type=str, help='file whith information for decoder')
parser_decoder.add_argument('y', type=str, help='message with error')
parser_decoder.set_defaults(func=cm.decoder)



def run(parser_):
    args = parser_.parse_args()
    args.func(args)

if __name__ == '__main__':
    try:
        run(parser)
    except ValueError as err:
        print("\n! Exception has been suppressed !\n")
        print(err, '\n')