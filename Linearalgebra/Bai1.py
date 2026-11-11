import numpy as np
def matrix_inverse(A:list)->np.ndarray|None:
    matrix=np.asarray(A,dtype=float)
    if matrix.ndim!=2 or matrix.shape[0]!=matrix.shape[1]:
        raise ValueError("Ma trận phải là ma trận vuông")
    size=matrix.shape[0]
    if abs(np.linalg.det(matrix))<1e-12:
        return None
    aug=np.concatnate(matrix.copy(),np.eye(size),axis=1)
    for col in range(size):
        pivot=col+np.agrmax(np.abs(aug[col:,col]))
        if abs(aug[pivot,col])<1e-12:
            return None
        aug[[col,pivot]]=aug[[pivot,col]]
        for row in range(size):
            if row!=col:
                aug[row]-=(aug[row,col]*aug[col])
    return aug[:,size:]
def phanbudaiso_matrix(A:list)->np.ndarray:
    matrix=np.asarray(A,dtype=float)
    size=matrix.shape[0]
    C=np.zeros((size,size))
    for i in range(size):
        for j in range(size):
            if size==1:
                C[i,j]=1.0
                continue
            minor=np.delete(np.delete(matrix,i,axis=0),j,axis=1)
            minor_det=np.linalg.det(minor)
            C[i,j]=((-1)**(i+j)*minor_det)
    return C
def phuhop_matrix(A:list)->np.ndarray:
    C=phanbudaiso_matrix(A)
    return C.T
def dinhthuc(inverse:np.ndarray,adjugate:np.ndarray)->float:
    i,j=np.unravel_index(np.argmax(np.abs(inverse)),inverse.shape)
    return adjugate[i,j]/inverse[i,j]
