def matchFind(corpus, keyword):
    A = corpus
    B = keyword
    C = A.split()
    D = B.split()
    Both = []
    for x in C:
        if x in D:
            Both.append(x)
    for x in range(len(Both)):
        Both[x]=str(Both[x])
    Final = []
    for x in set(Both):
        Final.append(x)
    MissingA =[]
    for x in C:
        if x not in Final and x not in MissingA:
            MissingA.append(x)
    for x in range(len(MissingA)):
        MissingA[x]=str(MissingA[x])
    MissingB = []
    for x in D:
        if x not in Final and x not in MissingB:
            MissingB.append(x)
    for x in range(len(MissingB)):
        MissingB[x]=str(MissingB[x])
    return Final
