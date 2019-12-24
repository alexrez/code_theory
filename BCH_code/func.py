import os
import signal
import errno
import math
import random
from itertools import combinations
from functools import wraps


# binominal coefficent
def c_n_k(n, k):
    tmp = k
    if (n - k) < k:
        tmp = n - k
    der = 1
    for j in range(tmp):
        der *= (n - j)
    return der / math.factorial(tmp)


def expected_value(p, n):
    sum_ = 0
    error_prob = 0
    for i in range(1, n + 1):
        error_prob = c_n_k(n, i) * p ** i * (1 - p) ** (n - i)
        sum_ += i * error_prob
    return math.ceil(sum_)


def get_combinations(lst, number):
    return list(combinations(lst, number))


def reduce_xor(l):
    res = l[0]
    for elem in l[1:]:
        res = res ^ elem
    return res


def hamming_weight(decimal):
    res = 0
    while decimal:
        res += decimal & 1
        decimal = decimal >> 1
    return res


def bit_counter(decimal):
    count = 0
    while decimal:
        count += 1
        decimal = decimal >> 1
    return count


def binary_mult(args):
    vec_a, vec_b = args
    res_vec = vec_a & vec_b
    return hamming_weight(res_vec) % 2


def to_decimal(binary):
    return sum(list(map(lambda x: x[1] << (len(binary) - 1 - x[0]), [(i, b) for i, b in enumerate(binary)])))


def poly_mult(poly_a, poly_b):
    result = 0
    len_poly_b = bit_counter(poly_b)
    for i in range(len_poly_b):
        if poly_b & (1 << i):
            result ^= poly_a << i
    return result


def poly_div(poly_a, poly_b):
    rem = poly_a
    len_rem = bit_counter(rem)
    len_poly_b = bit_counter(poly_b)
    result = 0
    while len_rem >= len_poly_b:
        shift = len_rem - len_poly_b
        rem ^= poly_b << shift
        result ^= 1 << shift
        len_rem = bit_counter(rem)
    return result, rem


def poly_pow(poly, power):
    len_poly = bit_counter(poly)
    result = 0
    for i in range(len_poly):
        if poly >> i & 1 == 1:
            result |= 1 << i * power
    return result


def number_power(number):
    counter = 0
    for i in reversed(number):
        if i > -1:
            return len(number) - 1 - counter
        counter += 1
    return 0


def random_error(n, t, length):
    errors = []
    for i in range(length):
        rand_error = [1 for _ in range(random.randint(0, t))]
        rand_error += [0] * (n - len(rand_error))
        random.shuffle(rand_error)
        errors.append(to_decimal(rand_error))
    return errors


def message_to_bin(text):
    return [ord(t) for t in text]


def message_to_ascii(bin_text):
    return [chr(b) for b in bin_text]


def split_message(text, k):
    bin_message = message_to_bin(text)
    off_set = 0
    message_to_encode = []
    block_mask = (1 << k) - 1
    len_m = 8

    for bin_m in bin_message:
        tmp_blocks = []
        new_off_set = (len_m - off_set) % k
        if new_off_set != 0:
            off_set_mask = (1 << new_off_set) -1
            tmp_blocks.append((bin_m & off_set_mask) << (k - new_off_set))
            bin_m = bin_m >> new_off_set

        for _ in range((len_m - new_off_set) // k):
            tmp_blocks.append(bin_m & block_mask)
            bin_m = bin_m >> k

        if off_set != 0:
            message_to_encode[-1] ^= bin_m

        message_to_encode += tmp_blocks[ : : -1]
        off_set = k - new_off_set

    return message_to_encode


def join_message(bin_text, k):
    # join_text = 1
    # for block in bin_text:
    #     join_text = join_text << k
    #     join_text ^= block

    # mask = (1 << len(bin_text) * k) - 1

    # len_m = 8
    # block_mask = (1 << len_m) - 1
    # len_text = math.ceil(len(bin_text) * k / len_m) - 1
    # print(len_text)
    # message_to_decode = [((join_text & mask) >> ((len_text - i) * len_m)) & block_mask  for i in range(1, len_text + 1)]
    # print('{0:b}\t'.format(join_text & mask), '|'.join(['{0:b}'.format(m) for m in message_to_decode]))
    # print(message_to_decode)

    off_set = 0
    message_to_decode = []
    len_m = 8
    i = 0

    for i_block in range(math.ceil(len(bin_text) * k / len_m)):
        block = 0
        new_off_set = (len_m - off_set) % k
        len_block = off_set
        
        if off_set != 0:
            block = message_to_decode.pop()
            if (len_block + k) < len_m:
                block = block << k
            else:
                block = block << (len_m - len_block)
        
        for j in range((len_m - off_set - new_off_set) // k):
            block |= bin_text[i]
            len_block += k
            print(len_block + k, (len_m - len_block))
            if (len_block + k) < len_m:
                block = block << k
            else:
                block = block << (len_m - len_block)
            i += 1
    
        if new_off_set != 0:
            block |= bin_text[i] >> (k - new_off_set)
            off_set_mask = (1 << (k - new_off_set)) -1
            bin_m = bin_text[i] & off_set_mask
            i += 1

        message_to_decode.append(block)

        if new_off_set != 0:
            message_to_decode.append(bin_m)
        off_set = (k - new_off_set) % k

        if i >= len(bin_text):
            break

    if message_to_decode[-1] == 0:
        message_to_decode = message_to_decode[:-1]

    return ''.join(message_to_ascii(message_to_decode))



