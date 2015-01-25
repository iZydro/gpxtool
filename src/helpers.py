def to_decimal(number, decimals=2):

    try:
        # Number casted to float, in case a string is coming
        number = float(number)

        divider = pow(10, decimals)
        integer = int(number)
        decimal = int((number - integer) * divider + 0.5)

        return str(integer) + "." + str(decimal)

    except:
        return "NaN"
