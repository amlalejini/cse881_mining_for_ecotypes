

def EditDistance(a, b):
    """
    a and b should be sequences in list form where each element is a symbol.
    """
    # Create DP table:
    #   * 1 Row for null character + each symbol of a
    #   * 1 Column for null character + each symbol of b
    table = [[None for _ in range(0, len(b) + 1)] for _ in range(0, len(a) + 1)]
    # Fill out the base case.
    for i in range(0, len(table[0])): table[0][i] = i
    for i in range(1, len(table)): table[i][0] = i
    # Fill out table row by row.
    for r in range(1, len(table)):
        for c in range(1, len(table[r])):
            achar = a[r - 1]
            bchar = b[c - 1]
            if achar == bchar:
                table[r][c] = table[r - 1][c - 1] # Bring down the top left.
            else:
                table[r][c] = min(table[r - 1][c - 1] + 1, table[r][c - 1] + 1, table[r - 1][c] + 1)
    return table[-1][-1]

def JaccardSimilarity(a, b):
    """
    a and b should be bitstrings of the same length.
    return the jaccard similarity between a and b: m11 / (m01 + m10 + m11)
    """
    assert(len(a) == len(b))
    m11 = 0
    m01 = 0
    m10 = 0
    for i in range(0, len(a)):
        if bool(int(a[i])) and bool(int(b[i])): m11 += 1
        elif bool(int(a[i])) and not bool(int(b[i])): m10 += 1
        elif not bool(int(a[i])) and bool(int(b[i])): m01 += 1
    return float(m11) / (m11 + m01 + m10)

def SimpleMatchingSimilarity(a, b):
    assert(len(a) == len(b))
    m11 = 0
    m01 = 0
    m10 = 0
    m00 = 0
    for i in range(0, len(a)):
        if bool(int(a[i])) and bool(int(b[i])): m11 += 1
        elif bool(int(a[i])) and not bool(int(b[i])): m10 += 1
        elif not bool(int(a[i])) and bool(int(b[i])): m01 += 1
        elif not bool(int(a[i])) and not bool(int(b[i])): m00 += 1
    return float(m11 + m00) / (m11 + m01 + m10 + m00)

if __name__ == "__main__":
    a = "1001"
    b = "1001"
    print a
    print b
    print JaccardSimilarity(a, b)
    print SimpleMatchingSimilarity(a, b)
    a = "1111"
    b = "0001"
    print a
    print b
    print JaccardSimilarity(a, b)
    print SimpleMatchingSimilarity(a, b)
    a = "1010"
    b = "0110"
    print a
    print b
    print JaccardSimilarity(a, b)
    print SimpleMatchingSimilarity(a, b)
    a = "aaaaaaaaaaaaaaaa"
    b = "bbbbb"
    print a
    print len(a)
    print b
    print len(b)
    print EditDistance(a, b)
