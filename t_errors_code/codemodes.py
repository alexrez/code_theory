import os
import pickle

from LinearCode import LinearCode


def gencode(args):
    linear_code = LinearCode(n=args.n, k=(args.n - args.r), d=(2 * args.t + 1))
    linear_code.make_code()
    print(linear_code)

    out_path = os.path.normpath(os.path.expanduser(args.out))
    with open(out_path, 'wb') as handle:
        pickle.dump(linear_code, handle, protocol=pickle.HIGHEST_PROTOCOL)

def coder(args):
    file_path = os.path.normpath(os.path.expanduser(args.inputfile))
    with open(file_path, 'rb') as handle:
        linear_code = pickle.load(handle)
    print('Loaded code information:\n{}'.format(linear_code))

    encoded_message, error = linear_code.coder(args.m, args.e)
    print("Encoded blocks of message whith errors:\t{}".format('|'.join(['{0:>0{width}b}'.format(m, width=linear_code._n) for m in encoded_message])))
    print("Error for each block of message:\t{}".format('|'.join(['{0:>0{width}b}'.format(e, width=linear_code._n) for e in error])))


def decoder(args):
    file_path = os.path.normpath(os.path.expanduser(args.inputfile))
    with open(file_path, 'rb') as handle:
        linear_code = pickle.load(handle)
    print('Loaded code information:\n{}'.format(linear_code))

    decoded_message, error = linear_code.decoder(args.y)
    print("Decoded blocks of message whith errors:\t{}".format('|'.join(['{0:>0{width}b}'.format(m, width=linear_code._k) for m in decoded_message])))
    print("Error for each block of message:\t{}".format('|'.join(['{0:>0{width}b}'.format(e, width=linear_code._n) for e in error])))


