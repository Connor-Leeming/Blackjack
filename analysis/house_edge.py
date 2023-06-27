import matplotlib.pyplot as plt
import numpy as np
from Data import outcome_tuples
import json


S = outcome_tuples()[:1_000_000]

S = [(x,y) for [x,y] in S]


S = np.reshape(S,(1000,1000,2))

"""means = [sample_mean(row) for row in S]


with open("means.json",'w+') as f:
    json.dump(means,f)"""


with open("means.json",'r') as f:
    means = json.load(f)

print(np.std(means,ddof=1))

# Increase figure size
plt.figure(figsize=(10, 6))

# Create histogram with better color and line width for edge
plt.hist(means, bins=50, color='skyblue', edgecolor='grey', linewidth=1.2)

mu = np.mean(means)
# Add vertical line for mean value
plt.axvline(
    x=mu, 
    color="crimson", 
    linestyle='--', 
    linewidth=2.5, 
    label="Mean: " + f"{round(mu,5)}" 
)

# Set grid
plt.grid(color='grey', linestyle='-', linewidth=0.25, alpha=0.5)

# Set title and labels
plt.title("Mean hand payout for 1,000 sub-samples", fontweight='bold', fontsize=12)
plt.xlabel("Mean hand payout", fontsize=13)
plt.ylabel('Count of sub-samples', fontsize=13)

# Add legend
plt.legend()

# Show the plot
plt.show()