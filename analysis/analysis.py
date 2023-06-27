from Data import outcome_tuples
import json
import numpy as np
import pandas as pd
import itertools
import matplotlib.pyplot as plt

def map_payouts(sample):
    # Define Omega

    X = ["Win", "Push", "Lose"]
    Y = ["Double", "Blackjack", "None"]
    Omega = [xy for xy in itertools.product(X,Y) if xy != ("Lose","Blackjack")]

    # Define pay scalars

    A, B = [1,0,-1], [2,1.5,1]
    X_to_A = {x : A[i] for i,x in enumerate(X)}
    Y_to_B = {y : B[i] for i,y in enumerate(Y)}

    # Define Payout Mappnig

    Payout_mapping = {
    (x,y) : (X_to_A[x] * Y_to_B[y]) for x,y in Omega
    }

    # map
    payout_sequence = [
        Payout_mapping[(x,y)] for [x,y] in sample
    ]

    return payout_sequence

def sample_mean(sample):
    payouts = map_payouts(sample)
    edge = (np.mean(payouts))
    return edge

def balance_time_series(sample,B0,bet):
    cumulative_payout = np.cumsum(map_payouts(sample))
    x = [i+1 for i,_ in enumerate(cumulative_payout)]
    y = (cumulative_payout*bet) + B0
    return (x,y)

def plot_series(data):
    # Create a new figure
    plt.figure(figsize=(10, 6))

    # Plot data with a black line
    plt.plot(*data, color='black')

    # Set the title, labels and grid
    plt.title("Balance Time Series")
    plt.xlabel("Hand number (millions)")
    plt.ylabel("Balance")

    # R-style white background
    plt.style.use('seaborn-whitegrid')

    # Set gridlines
    plt.grid(True, color='grey', linestyle='--', linewidth=0.5)

    plt.show()

"""S = outcome_tuples()[:1_000_000]

S = [(x,y) for [x,y] in S]


S = np.reshape(S,(1000,1000,2))


means = [sample_mean(row) for row in S]


with open("means.json",'w+') as f:
    json.dump(means,f)
"""

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
