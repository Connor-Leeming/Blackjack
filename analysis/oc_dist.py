import matplotlib.pyplot as plt
import numpy as np
import json
from collections import Counter

with open('testsamp.json','r') as f:
    s = json.load(f)

tups = [tuple(item) for item in s]

data = dict(Counter(tups))

X,Y = [],[]
for x,y in sorted(data.items(),key=lambda x: x[1],reverse=True):
    X.append(x); Y.append(y)
Y = [y/sum(Y) for y in Y]

labels = [f"({str(x)},{str(y)})" for (x,y) in X]
colors = []
for x,_ in X:
    if x == "Win":
        colors.append("#006400")  # Dark Green
    elif x == "Push":
        colors.append("#FFD700")  # Gold
    else:
        colors.append("#8B0000")  # Dark Red

# Increase figure size for better visibility
plt.figure(figsize=(10, 6))

# Specify bar color, edgecolor
plt.bar(
    labels,
    Y,
    color=colors,
    edgecolor='blue',
    alpha =0.7,
    zorder=10
)

# Add grid lines
plt.grid(color='#95a5a6', linestyle='--', linewidth=2, axis='y', alpha=0.7)

# Set background color
plt.gca().set_facecolor('#ecf0f1')

# Rotate x-labels by 45 degrees
plt.xticks(rotation=45)

# Add labels and title
plt.xlabel('Outcome and Type')
plt.ylabel('Frequency')
plt.title('Blackjack Outcome Frequencies')

plt.tight_layout()
plt.show()

