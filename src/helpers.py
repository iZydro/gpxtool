def to_decimal(number, decimals=2):

    try:
        # Number casted to float, in case a string is coming
        number = float(number)

        divider = pow(10, decimals)
        integer = int(number)
        decimal = ""

        if decimals > 0:
            decimal = "." + str(int((number - integer) * divider + 0.5))

        return str(integer) + decimal

    except:
        return "NaN"
