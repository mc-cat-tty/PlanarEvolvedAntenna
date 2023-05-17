import pickle
from manim import *
from os.path import join
from typing import List
from utils.geometry import Segment

OUTPUT_DIRECTORY = "results"

class RodIncrementalGen(Scene):
  def construct(self):
    epoch = 3
    coordZ = [0]

    generationSegments = List[List[Segment]]
    with open(join(OUTPUT_DIRECTORY, f"epoch_{epoch}.pkl"), "rb") as f:
      generationSegments = pickle.load(f)
    
    p = Polygon(*[segment + coordZ for segment in generationSegments[0]])
    self.add(p)