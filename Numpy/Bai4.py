import numpy as np
def cosine_similarity(A, B):
    arraya=np.array(A)
    arrayb=np.array(B)
    total=np.sum(arraya*arrayb,axis=1)
    norma=np.linalg.norm(arraya,axis=1)
    normb=np.linalg.norm(arrayb,axis=1)
    return total/(norma*normb)