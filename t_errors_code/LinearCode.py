import random
import json
from itertools import zip_longest

import func

class LinearCode():

    def __init__(self, n, k, d, channel_error_prob=0.005):
        if (n - k <= 0) or (n - k >= n) or (d <= 0) or ((d - 1) // 2 > n):
            raise ValueError('Only allows 0 < r < n and 0 < t <= n')
        if not func.gvb(n, k, d):
            raise ValueError('The condition of the "Gilbert-Varshamov bound" theorem is not fulfilled. (n={}, k={}, d={})'.format(n, k, d))
        self._n = n
        self._k = k
        self._r = self._n - self._k
        self._d = d
        self._p = channel_error_prob
        self.decode_error_prob = func.error_probability(self._p, self._n, self._d)


    def make_A_matrix(self):
        A_matrix_t = []
        linear_comb = func.get_combinations(self._d, self._r)
        illegal_vectors = set(map(func.reduce_xor, linear_comb))
        # legal_vectors = [i for i in range(1, (1 << self._r)) if i not in illegal_vectors]
        # for i in range(self._k):
        #     if not legal_vectors:
        #         i = 0
        #         illegal_vectors = set(map(func.reduce_xor, linear_comb))
        #         legal_vectors = [i for i in range(1, (1 << self._r)) if i not in illegal_vectors]

        #     new_vector = legal_vectors[random.randint(0, len(legal_vectors) - 1)]
        #     A_matrix_t.append(new_vector)

        #     if (self._d - 1 > 2):
        #         func.update_combinations(new_vector, legal_vectors, illegal_vectors)
        #     illegal_vectors.add(new_vector)

        #     if new_vector in legal_vectors:
        #         legal_vectors.remove(new_vector)

        for i in range(self._k):
            new_vector = random.randint(3, (1 << self._r) - 1)
            while new_vector in illegal_vectors:
                new_vector = random.randint(3, (1 << self._r) - 1)
            A_matrix_t.append(new_vector)

            if (self._d - 1 > 2):
                func.update_combinations(new_vector, illegal_vectors)
            illegal_vectors.add(new_vector)

        # A_matrix_t = [5, 6, 7, 3]
        self._A_matrix = func.transpose_matrix(A_matrix_t, self._r)


    def make_H_matrix_t(self):
        self.make_A_matrix()
        self._H_matrix_t = []
        for i, column in enumerate(self._A_matrix):
            self._H_matrix_t.append((column << self._r) | (1 << self._r - 1 - i))


    def make_G_matrix(self):
        self.make_H_matrix_t()


    def make_S_vector(self):
        vectors_weight = dict()
        for i in range(1 << self._n):
            w_i = func.hamming_weight(i)
            if w_i <= (self._d - 1) // 2:
                vectors_weight.setdefault(w_i, []).append(i)
        vectors_leaders = [v for val in vectors_weight.values() for v in val]

        self._S_vector = dict()
        self._S_vector[0] = [0]

        for leader in vectors_leaders:
            syndrome = self.__get_syndrome(leader)
            if syndrome > 0:
                self._S_vector.setdefault(syndrome, []).append(leader)
    

    def __get_codeword(self, message):
        zip_vec = (zip_longest(self._A_matrix, [message], fillvalue=message))
        return message << self._r | func.to_decimal(list(map(func.binary_mult, list(zip_vec))))


    def __get_syndrome(self, y):
        zip_vec = (zip_longest(self._H_matrix_t, [y], fillvalue=y))
        return func.to_decimal(list(map(func.binary_mult, list(zip_vec))))


    def make_code(self):
        self.make_G_matrix()
        self.make_S_vector()


    def coder(self, message, error):
        message_to_encode = [int(message[i: i + self._k], 2) for i in range(0, len(message), self._k)]
        if error is None:
            errors = func.random_error(self._n, (self._d - 1) // 2, len(message_to_encode))
        else:
            if len(error) > self._n:
                raise ValueError('Lenght of error in binary should be n bites or less')
            errors = [int(error, 2)] * len(message_to_encode)

        return [self.__get_codeword(m) ^ e for m, e in zip(message_to_encode, errors)], errors


    def decoder(self, message):
        message_to_decode = [int(message[i: i + self._n], 2) for i in range(0, len(message), self._n)]
        errors = [self._S_vector.get(self.__get_syndrome(m), [])[0] for m in message_to_decode]
        return [(m ^ e) >> self._r for m, e in zip(message_to_decode, errors)], errors


    def __repr__(self):
        A_matrix_t = func.transpose_matrix(self._A_matrix, self._k)
        G_to_print = [i | a for i, a in zip([1 << (self._n - 1 - j) for j in range(self._k)], A_matrix_t)]

        G_to_print = '[\n ' +\
                     '\n '.join(['{0:0>{width}b}'.format(row, width=self._n) for row in G_to_print]) +\
                     '\n]'

        S_to_print = '{\n ' +\
                     '],\n '.join('{0:0>{width}b}'.format(k, width=self._r) +\
                     ':\t[' +\
                     ', '.join(['{0:0>{width}b}'.format(i, width=self._n) for i in v]) for k, v in self._S_vector.items()) +\
                     ']\n}'

        return('\nG matrix:\n{}\n\nDecoding vector:\n{}\n\nDecoder error probability:\n{}\n'.format(G_to_print,
                                                                                                    S_to_print,
                                                                                                    '{0:.4}'.format(self.decode_error_prob)))



