def print_frac(frac):
    denominator = frac.denominator
    if denominator == 1:
        return str(frac.numerator)
    while denominator % 2 == 0:
        denominator //= 2
    while denominator % 5 == 0:
        denominator //= 5
    if denominator == 1:
        return str(frac.numerator / frac.denominator)
    return "/".join((str(frac.numerator), str(frac.denominator)))


def print_coef(coef):
    res = ""
    if coef != 1:
        res = str(coef)
        if not coef.numerator.real:
            res = res.join("()")
    if coef == -1:
        res = "-"
    return res
