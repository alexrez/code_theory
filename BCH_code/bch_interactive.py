import argparse

from BCHcode import BCH
import func

parser = argparse.ArgumentParser(prog='BCHcode', usage='%(prog)s mode param',
                                 description='BCH error-correcting code.')

parser.add_argument('p', type=float, help='channel parametr')
parser.add_argument('n', type=int, help='length of a message\'s block')

exceptions =  (ValueError, TimeoutError)

if __name__ == '__main__':
    args = parser.parse_args()

    try:
        bch_code = BCH(args.p, args.n)
        bch_code.make_code()
        print(bch_code)

        while True:
            message = input('Enter a message: ')

            print('\nEncoding:')
            bin_message, encoded_message = bch_code.encode(message)
            for bin_m, enc_m in zip(bin_message, encoded_message):
                print('message\'s block: {0:>0{width_0}b}\t<>\tcodeword: {1:>0{width_1}b}'.
                    format(bin_m, enc_m, width_0=bch_code._k, width_1=bch_code._n))

            print('\nSending message:')
            errors = func.random_error(bch_code._n, bch_code._t, len(encoded_message))
            message_to_decode = []
            for m, e in zip(encoded_message, errors):
                message_to_decode.append(m ^ e)
                print('codeword: {0:>0{width}b}\t<>\terror: {1:>0{width}b}\t<>\tresult: {2:>0{width}b}'.
                    format(m, e, m ^ e, width=bch_code._n))

            print('\nDecoding:')
            decoded_message, found_errors = bch_code.decode(message_to_decode)
            for i in range(len(message_to_decode)):
                print('encoded: {0:>0{width}b}\t<>\terror: {1:>0{width}b}\t<>\tdecoded: {2:>0{width_d}b}\t<>\tstatus: {3}'.
                    format(message_to_decode[i], found_errors[i], decoded_message[i], 'OK' if bin_message[i] == decoded_message[i] else 'FAIL',
                        width=bch_code._n, width_d=bch_code._k))

            print('\nResult:')
            int_mes, str_message = func.join_message(decoded_message, bch_code._k)
            print('Binary: {}\nASCII: {}'.format(''.join(['{0:b}'.format(m) for m in int_mes]), str_message))

            print('\n\t======\tOne more cycle\t=====\n')

    except exceptions as err:
        print("\n{}\n".format(err))

    except KeyboardInterrupt as err:
        print("\nProgramm is shuttitg down\n")
