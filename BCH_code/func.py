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


def bin_to_str(bin_text, width):
    return ''.join(['{0:>0{w}b}'.format(t, w=width) for t in bin_text])


def split_message(text, k):
    bin_message = message_to_bin(text)
    len_m = 8
    concat_mes = bin_to_str(bin_message, len_m)
    split_mes = [concat_mes[i: i + k] for i in range(0, len(concat_mes), k)]

    if len(split_mes[-1]) < k:
        split_mes[-1] += '0' * (k - len(split_mes[-1]))
    return  list(int(m, 2) for m in split_mes)


def join_message(bin_text, k):
    concat_mes = bin_to_str(bin_text, k)
    len_m = 8
    message_to_decode = [int(concat_mes[i: i + len_m], 2) for i in range(0, len(concat_mes), len_m)]
    
    while message_to_decode[-1] == 0:
        message_to_decode = message_to_decode[:-1]
    return message_to_decode, ''.join(message_to_ascii(message_to_decode))



