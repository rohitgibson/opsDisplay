from itertools import combinations, permutations

test_nCr = combinations([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 3)

test_nPr_larg = permutations([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 4)
test_nPr_norm = permutations([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 3)
test_nPr_smol = permutations([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 2)

for i in test_nCr:
    print(i)

for x in test_nPr_larg:
    print(x)