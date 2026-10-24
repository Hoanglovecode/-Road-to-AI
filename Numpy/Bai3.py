import numpy as np
def mse_loss(y_true,y_pred):
    Y_true=np.array(y_true)
    Y_pred=np.array(y_pred)
    total=(Y_true-Y_pred)**2
    return np.mean(total)