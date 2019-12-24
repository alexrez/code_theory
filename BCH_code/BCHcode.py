import os
import math
import json
import copy
from itertools import zip_longest

import func

class BCH():

    def __init__(self, p, n, file=None):
        if file is None:
            self._file = os.path.normpath(os.path.expanduser('primpoly.txt'))
        else:
            self._file = os.path.normpath(os.path.expanduser(file))
        self.get_params(p, n)
        self._d = 2 * self._t + 1
        self._k = self._n - self._t * self._m

        if (self._k < 0):
            raise ValueError('Can\'t construct BCH code with conditions of p = {} and n = {}'.format(p, n))


    def get_params(self, p, n):
        if (p < 0) or (p > 1/2) or (n < 1):
            raise ValueError('Only allows 0 < p < 1/2, n >= 1')

        power = func.bit_counter(n)
        if func.hamming_weight(n + 1) != 1:
            power -= 1
            n = (1 << power) - 1

        tmp_t = func.expected_value(p, n)
        while (power > 2) and (n - tmp_t * power) <= 0:
            power -= 1
            n = (1 << power) - 1
            tmp_t = func.expected_value(p, n)

        self._n = n
        self._m = power
        self._t = tmp_t


    def make_prime_polynom(self):
        pr_polynoms = []
        self._prime_poly = None
        with open(self._file, 'r') as handle:
            pr_polynoms = map(int, handle.read().split(', '))

        for poly in pr_polynoms:
            if poly > 1 << (self._m + 1):
                break
            elif (self._prime_poly is None) and (poly > 1 << self._m):
                self._prime_poly = poly
        del pr_polynoms


    def make_GF(self):
        self.make_prime_polynom()

        self._GF = [0] * (self._n + 1)
        self._GF[0] = 1
        self._logGF = [0] * (self._n + 1)

        for i in range(1, self._n + 1):
            tmp = (self._GF[i - 1] << 1)
            if tmp > self._n:
                tmp = tmp ^ self._prime_poly
            self._GF[i] = tmp
            self._logGF[tmp] = i

        self._logGF[0] = -1
        self._logGF[1] = 0


    def make_cyclotomic_classes(self):
        self.cyclotomic_classes = []
        used_s = set()
        used_s.add(0)
        s = 1
        
        while len(used_s) < self._n:
            while s in used_s:
                s += 1
            tmp_class = [s]
            used_s.add(s)
            shift = 1
            ind_to_append = s * (1 << shift) % self._n

            while ind_to_append != s:
                tmp_class.append(ind_to_append)
                used_s.add(ind_to_append)
                shift += 1
                ind_to_append = s * (1 << shift) % self._n

            self.cyclotomic_classes.append(tmp_class)
        del used_s


    def make_M_i_polynom(self):
        self.make_cyclotomic_classes()

        self._M_poly = []
        for i in range(2 * self._t):
            poly_power = len(self.cyclotomic_classes[i])
            M_poly = 1 << poly_power

            for j in range(poly_power):
                linear_comb = list(map(lambda x: self._GF[sum(x) % self._n], func.get_combinations(self.cyclotomic_classes[i], j + 1)))
                M_poly ^= func.reduce_xor(linear_comb) << poly_power - j - 1

            self._M_poly.append(M_poly)


    def make_g_x(self):
        self.make_M_i_polynom()
        
        self._g_x = self._M_poly[0]
        for i in range(1, self._t): # 2t - 1 without even memders => t members
            self._g_x = func.poly_mult(self._g_x, self._M_poly[i])


    def make_code(self):
        self.make_GF()
        self.make_g_x()


    def encode(self, message):
        bin_message = func.split_message(message, self._k)
        encoded_message = [bm << (self._n - self._k) for bm in bin_message]
        return bin_message, [mes | func.poly_div(mes, self._g_x)[1] for mes in encoded_message]


    def make_S_vector(self, message):
        self._S_vector = [0] * (2 * self._t + 1)
        for i, c_class in enumerate(self.cyclotomic_classes):
            for alpha_power in c_class:
                if alpha_power < 2 * self._t + 1:
                    syndrome = func.poly_pow(func.poly_div(message, self._M_poly[i])[1], alpha_power)
                    if func.bit_counter(syndrome) >= func.bit_counter(self._prime_poly):
                        syndrome = func.poly_div(syndrome, self._prime_poly)[1]
                    
                    self._S_vector[alpha_power] = self._logGF[syndrome]


    def algorithm_Berlekamp_Messey(self, message):
        sigmas = []
        for mes in message:
            self.make_S_vector(mes)

            lambdas = [[0] * self._d] * self._d
            lambdas[0][0] = 1
            lambdas[-1][0] = 1
            Ls = [0] * self._n
            deltas = [0] * self._d
            deltas[0] = 1

            for k in range(1, self._d):
                for i in range(Ls[k - 1] + 1):
                    if (k - i < len(self._S_vector)) and (self._S_vector[k - i] >= 0) and (lambdas[k - 1][i] > 0):
                        deltas[k] ^= self._GF[(self._logGF[lambdas[k - 1][i]] + self._S_vector[k - i]) % self._n]
                
                m = [i for i in range(k) if Ls[i] == Ls[k - 1]][0]
                lambdas[k] = lambdas[k - 1].copy()
                if deltas[k] == 0:
                    Ls[k] = Ls[k - 1]
                else:
                    c_l = [0] * (self._d + k - m)
                    for i in range(self._d):
                        if lambdas[m - 1][i] > 0:
                            c_l[i + k - m] = self._GF[(self._logGF[lambdas[m - 1][i]] +\
                                self._logGF[deltas[k]] + self._n - self._logGF[deltas[m]]) % self._n]

                    c_l += [0 for _ in range(self._d - len(c_l))]
                    lambdas[k] = [lambdas[k][i] ^ c_l[i] for i in range(self._d)]
                    Ls[k] = max(Ls[k - 1], Ls[m - 1] + k - m)

            sigmas.append([self._logGF[i] for i in lambdas[2 * self._t]])
        return sigmas


    def make_position_vector(self, sigma):
        error_vec = [0] * self._n
        sigma_power = func.number_power(sigma) + 1
        for i in range(self._n):
            result = self._GF[sigma[0]]
            for power in range(1, sigma_power):
                if sigma[power] >= 0:
                    result ^= self._GF[(sigma[power] + i * power) % self._n]
            if result == 0:
                error_vec[(self._n - i) % self._n] = 1
        return error_vec[ : : -1]


    def get_errors(self, bin_message):
        sigmas = self.algorithm_Berlekamp_Messey(bin_message) 
        return list(map(func.to_decimal, [self.make_position_vector(sigma) for sigma in sigmas]))


    def decode(self, bin_message):
        errors = self.get_errors(bin_message)
        return [(m ^ e) >> (self._n - self._k) for m, e in zip(bin_message, errors)], errors
        

    def __repr__(self):
        param_to_print = 'Code parametrs:\n\tt = {}\n\tn = {}\n\tk = {}'.format(self._t, self._n, self._k)
        g_x_to_print = '\n\tg(x) = {0:b}\n'.format(self._g_x)
        return ''.join([param_to_print, g_x_to_print])




