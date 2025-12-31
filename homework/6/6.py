def det_recursive(A):
    n = len(A)

    if n == 1:
        return A[0][0]

    if n == 2:
        return A[0][0]*A[1][1] - A[0][1]*A[1][0]

    det = 0
    for j in range(n):
        sub = [row[:j] + row[j+1:] for row in A[1:]]
        det += ((-1)**j) * A[0][j] * det_recursive(sub)

    return det

M = [
    [1, 2, 3],
    [0, 4, 5],
    [1, 0, 6]
]

print("Determinant =", det_recursive(M))
