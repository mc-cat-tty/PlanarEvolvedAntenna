import pickle
from os.path import join
from core.population import Population

OUTPUT_DIRECTORY = "results"

def loadPop(epoch: int) -> Population:
  with open(join(OUTPUT_DIRECTORY, f"epoch_{epoch}.pkl"), "rb") as f:
    pop: Population = pickle.load(f)
  return pop