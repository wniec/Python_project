def precedes(first, second):
    return first[0] <= second[0] and first[1] <= second[1]


def follows(first, second):
    return first[0] >= second[0] and first[1] >= second[1]


def add(first, second):
    return first[0] + second[0], first[1] + second[1]


def subtract(first, second):
    return first[0] - second[0], first[1] - second[1]
