from strictyaml import ScalarValidator

import math
#complex_cartesian_regex=r"(\+|-)?[0-9]+(\.[0-9]+)?(\+|-)[0-9]+(\.[0-9]+)?i"
#complex_polar_regex=r"\(\+?[0-9]+(\.[0-9]+)?, ?(\+|-)?[0-9]+(\.[0-9]+)?\)"
#complex_number_regex="({})|({})".format(complex_cartesian_regex,
#        complex_polar_regex)

"""
Validates a complex number input
"""
class Complex(ScalarValidator):
    def validate_scalar(self, chunk):
        val=chunk.contents
        val=val.strip() # whitespace
        has_paren=(val[0]=='(' and val[-1]==')')
        try:
            if has_paren:
                val=val[1:-1]
            val = val.replace("i","j")
            return complex(val)
        except ValueError:
            if has_paren:
                try:
                    magnitude,angle = tuple(val.split(","))
                    magnitude = float(magnitude)
                    angle = float(angle)*2*math.pi
                    return magnitude*math.cos(angle)+\
                        1j*magnitude*math.sin(angle)
                except ValueError:
                    chunk.expecting_but_found("when expecting a complex number")
            else:
                chunk.expecting_but_found("when expecting a complex number")