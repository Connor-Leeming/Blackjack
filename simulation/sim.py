import argparse
from simulation import Simulate as sim

parser = argparse.ArgumentParser()
parser.add_argument("n", help="The number of hands to simulate", type=int)
args = parser.parse_args()
sim(args.n)
