#!/usr/bin/env python3

import pickle
from os.path import join
from config import Config
from core.population import Population

CONFIG_FILENAME = "config.yaml"
OUTPUT_DIRECTORY = "results"

if __name__ == "__main__":
  with open(CONFIG_FILENAME, "r") as f:
    Config.loadYaml(f)

  pop = Population()
  for generation, epoch in pop.generations():
    print(generation)
    with open(join(OUTPUT_DIRECTORY, f"epoch_{epoch}.pkl"), "wb") as f:
      pickle.dump([
        [
          list(segment.toList()[i])
          for i in range(2)
          for segment in gene.getCartesianCoords()
        ] for gene in generation
      ], f)