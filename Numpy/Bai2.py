import numpy as np

def stable_softmax(logits):
    maxlogits=np.max(logits,axis=1,keepdims=True)
    sumlogits=np.sum(np.exp(logits-maxlogits),axis=1,keepdims=True)
    return np.exp(logits-maxlogits)/sumlogits

