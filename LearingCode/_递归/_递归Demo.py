def sum(num):
    if num == 1:
        return 1
    return num + sum(num - 1)


if __name__ == '__main__':
    result = sum(3)
    print(result)
