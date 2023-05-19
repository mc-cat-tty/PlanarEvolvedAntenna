import pickle
import random
from tkinter import BOTTOM
from turtle import circle
from manim import *
from os.path import join
from typing import List
from core.population import Population
from core.gene import Gene
from config import Config

OUTPUT_DIRECTORY = "results"
SCALE_K = 15

class Intro(ZoomedScene):
  def construct(self):
    title = Text("Planar Evolved Antenna")
    subtitle = Text(
      "Genetic algorithm for radiation pattern optimization",
      t2c={
        "Genetic algorithm": BLUE,
        "radiation pattern": BLUE
      }
    )
    
    self.play(
      Create(title)
    )
    self.wait()


    self.play(
      Transform(title, subtitle),
      self.camera.frame.animate.scale(1.3)
    )
    self.wait()

    self.play(
      Uncreate(title)
    )
    self.wait()

class RodIncrementalGen(MovingCameraScene):
  def speedRamp(self, x: float) -> float:
    center = 1
    plateau = 0.3
    scaleY = 3
    return np.exp(- (x - center)) / scaleY + plateau

  def createGene(self, gene: Gene, id: int, speedFactor: float) -> VGroup:
    coordZ = (0,)
    generationSegments = [
      segment.toList()
      for segment in gene.getCartesianCoords()
    ]

    polychain = [
      Line(
        np.array(geneSegment[0] + coordZ) / SCALE_K,
        np.array(geneSegment[1] + coordZ) / SCALE_K,
        stroke_color=GREEN_C,
        stroke_width=70/SCALE_K
      )
      for geneSegment in generationSegments
    ]

    self.play(Transform(self.geneIdTxt, Text(f"Gene ID: {id}").to_corner(UL)))

    [self.play(Create(segment), run_time=0.51 * speedFactor * random.random()) for j, segment in enumerate(polychain)]
    self.wait()

    return VGroup(*polychain)


  def construct(self):
    with open("config.yaml", "r") as f:
      Config.loadYaml(f)

    epoch = 3
    geneId = 0
    self.geneIdTxt = Text(f"Gene ID: {geneId}").to_corner(UL)
    self.validTxt = Text("Valid?").next_to(self.geneIdTxt, DOWN)

    """
    Show problem constraints
    """
    outerCircle = Circle(radius=33/SCALE_K)
    innerCircle = Circle(radius=2.5/SCALE_K)
    innerCircle.shift((5.6 / SCALE_K, 0, 0))
    self.play(
      Write(
        Cutout(
          outerCircle,
          innerCircle,
          fill_opacity=0.5,
          color=BLUE,
          stroke_color=RED,
          stroke_width=40/SCALE_K
        ),
        run_time=2
      ),
      Write(
        self.geneIdTxt,
        run_time=2
      ),
      Write(
        self.validTxt,
        run_time=2
      )
    )
    self.wait()

    """
    Load population and show some good gene generation
    """
    with open(join(OUTPUT_DIRECTORY, f"epoch_{epoch}.pkl"), "rb") as f:
      pop: Population = pickle.load(f)

    for i in range(geneId, 2):
      speedFactor = self.speedRamp(i)

      g = self.createGene(pop.population[i], geneId, speedFactor)

      self.play(
        Indicate(self.validTxt, color=GREEN),
      )

      self.play(FadeOut(g), run_time=0.7 * speedFactor)
      self.wait()
      geneId += 1

    """
    Load wrong genes and show their generation and denstruction
    """
    with open(join(OUTPUT_DIRECTORY, f"invalid_{epoch}.pkl"), "rb") as f:
      invalids: List[Gene] = pickle.load(f)
    
    invalidIdxs = [
      0,  # Circle breaker
      94,  # Inner hole intersecter
      30  # Self intersecter
    ]
    for idx in invalidIdxs:
      g = self.createGene(invalids[idx], geneId, 1)

      self.play(
        Indicate(self.validTxt, color=RED),
      )

      [self.play(FadeToColor(g, color = RED if i%2 == 0 else GREEN), run_time=0.3) for i in range(4)]

      self.play(
        Uncreate(g),
        FadeToColor(g, color=RED),
        run_time=0.3
      )
      self.wait()

      geneId += 1
    
    for i in range(geneId, 100):
      speedFactor = self.speedRamp(i) * 0.1

      g = self.createGene(pop.population[i], geneId, speedFactor)

      self.play(
        Indicate(self.validTxt, color=GREEN),
      )

      self.play(FadeOut(g), run_time=0.7 * speedFactor)
      self.wait()
      geneId += 1