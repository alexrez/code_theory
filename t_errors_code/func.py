import math
from itertools import combinations
import random


# binominal coefficent
def c_n_k(n, k):
    tmp = k
    if (n - k) < k:
        tmp = n - k
    der = 1
    for j in range(tmp):
        der *= (n - j)
    return der / math.factorial(tmp)


# gilbert_varshamov_bound
def gvb(n, k, d):
    columns = 0
    for i in range(d - 1):
        columns += c_n_k(n - 1, i)
    return columns < (1 << (n - k))


def error_probability(p, n, d):
    t = (d - 1) // 2
    error_prob = 0
    for i in range(t + 1):
        error_prob += c_n_k(n, i) * p ** i * (1 - p) ** (n - i)
    return 1 - error_prob


def get_combinations(d, r):
    el_combinations = []
    for i in range(1, d - 1):
        el_combinations += (list(combinations([1 << (r - 1 - j) for j in range(r)], i)))
    return el_combinations


def update_combinations(elem, vector_to_decrease, vector_to_increase):
    tmp_set = set()
    for vec in vector_to_increase:
        new_comb = elem ^ vec
        tmp_set.add(new_comb)
        if new_comb in vector_to_decrease:
            vector_to_decrease.remove(new_comb)
    vector_to_increase.update(tmp_set)


def reduce_xor(l):
    res = l[0]
    for elem in l[1:]:
        res = res ^ elem
    return res


def transpose_matrix(matrix, size):
    matrix_t = [0] * size
    n = len(matrix) - 1
    for i, column in enumerate(matrix):
        for row in range(size):
            mask = 1 << row
            matrix_t[size - 1 - row] += int((column & mask) == mask) << (n - i)
    return matrix_t


def hamming_weight(decimal):
    res = 0
    while decimal:
        res += decimal & 1
        decimal = decimal >> 1
    return res


def binary_mult(args):
    vec_a, vec_b = args
    res_vec = vec_a & vec_b
    return hamming_weight(res_vec) % 2


def to_decimal(binary):
    return sum(list(map(lambda x: x[1] << (len(binary) - 1 - x[0]), [(i, b) for i, b in enumerate(binary)])))


def random_error(n, t, length):
    errors = []
    for i in range(length):
        rand_error = [1 for _ in range(random.randint(0, t))]
        rand_error += [0] * (n - len(rand_error))
        random.shuffle(rand_error)
        errors.append(to_decimal(rand_error))
    return errors



