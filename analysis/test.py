import random
import numpy as np

A = np.array([random.randint(0,100) for x in range(100)])
B = np.reshape(A,(10,10))

rowmeans = [np.mean(row) for row in B]

print(np.mean(A))
print(np.mean(rowmeans))

print(np.std(A))
print(np.std(rowmeans))