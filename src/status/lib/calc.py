
# This is a function meant to find the
# calculated value for testing at the status
def calc(values, operators):

    ret = values[0]

    for i in range(1,len(values)):
        op = operators[i-1]

        if(op == '+'):
            ret += values[i]
        elif(op == '-'):
            ret -= values[i]
        elif(op == '*'):
            ret *= values[i]
        elif(op == '/'):
            ret /= values[i]

    return ret
