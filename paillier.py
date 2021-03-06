#!/usr/bin/env python
import struct
import utils

KEY_LENGHT = 4096

def inverse(a, n):
    """Find the inverse of a modulo n if it exists"""
    t = 0
    newt = 1
    r = n
    newr = a
    while newr != 0:
        quotient = int((r - (r % newr)) / newr)
        tt = t
        t = newt
        newt = tt - quotient * newt
        rr = r
        r = newr
        newr = rr - quotient * newr
    if r > 1:
        return "a is not invertible"
    if t < 0:
        t = t + n
    return t

def lcm(a, b):
    """Computing the least common multiple between a and b"""
    n = a * b
    if n < 0:
        n = n * -1
    return int(n / utils.nonrec_gcd(a, b))

def L(x, n):
    return int((x - 1) / n)

def key_gen(p, q):
    if utils.nonrec_gcd(p, q) != 1:
        # non-distinct
        exit(1)
    n = p * q
    g = n + 1
    lmdba = (p-1) * (q-1)
    mu = utils.invert(lmdba, n)
    return (n, g), (n, p, q, g, lmdba, mu)

def gen_key():
    p = utils.getprimeover(KEY_LENGHT>>1)
    q = utils.getprimeover(KEY_LENGHT>>1)
    return key_gen(p, q)

def R_old(n):
    with open("/dev/urandom", 'rb') as f:
        r = struct.unpack(">Q", f.read(8))[0] % n
        return r

def R(n):
    return utils.randomnumber(n)
    while True:
        r = utils.randomnumber(n)
        if utils.nonrec_gcd(r, n) == 1:
            return r

def encrypt(m, pub):
    n, g = pub
    n2 = n * n
    r = R(n)
    return (utils.powmod(g, m, n2) * utils.powmod(r, n, n2)) % n2, r

def decrypt(c, priv):
    n, p, q, g, lmdba, mu = priv
    n2 = n * n
    return L(utils.powmod(c, lmdba, n2), n) * mu % n

def mult(cipher, scalar, n2):
    return utils.powmod(cipher, scalar, n2)

def add(c1, c2, n2):
    return c1 * c2 % n2

if __name__ == "__main__":
    # print(KEY_LENGHT>>1)
    p = utils.getprimeover(KEY_LENGHT>>1)
    q = utils.getprimeover(KEY_LENGHT>>1)
    # print(p)
    # print(q)

    # http://www.primos.mat.br/primeiros_10000_primos.txt
    pub, priv = key_gen(p, q)
    n, p, q, g, lmdba, mu = priv
    n2 = n * n

    # print(pub, priv)

    s1 = 180
    s2 = 10
    
    print(s1)
    print(s2)
    c1, r1 = encrypt(s1, pub)
    c2, r2 = encrypt(s2, pub)
    # print(c1)
    # print(c2)

    # Homomorphic properties
    cadd = c1 * c2 % n2
    # print(cadd)
    cmult = utils.powmod(c1, 20, n2)
    # print(cmult)

    # (180 + 10) * 10 + 180 = 2'080
    test = add(mult(add(c1, c2, n2), 10, n2), c1, n2)
    # 180 * 100 + 180 * 100 = 36'000
    test2 = add(mult(c1, 100, n2), mult(c1, 100, n2), n2)

    madd = decrypt(cadd, priv)
    mmult = decrypt(cmult, priv)
    mtest = decrypt(test, priv)
    mtest2 = decrypt(test2, priv)
    m1 = decrypt(c1, priv)
    m2 = decrypt(c2, priv)

    print("add c1 + c2:", madd)
    print("mult c1 * 20:", mmult)
    print("test composition:", mtest)
    print("test composition 2:", mtest2)
    print(decrypt(encrypt(10, pub)[0], priv))
