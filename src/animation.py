import pickle
from tkinter import CENTER
from turtle import width
from manim import *
from os.path import join
from typing import List
from utils.geometry import Segment

OUTPUT_DIRECTORY = "results"

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

  def construct(self):
    epoch = 4
    coordZ = (0,)

    generationSegments = List[List[Segment]]
    with open(join(OUTPUT_DIRECTORY, f"epoch_{epoch}.pkl"), "rb") as f:
      generationSegments = pickle.load(f)

    outerCircle = Circle(radius=33)
    innerCircle = Circle(radius=2.5)
    innerCircle.shift((5.6, 0, 0))
    self.play(
      self.camera.frame.animate.scale(10),
      Write(
        Cutout(
          outerCircle,
          innerCircle,
          fill_opacity=0.5,
          color=BLUE,
          stroke_color=RED,
          stroke_width=40
        ),
        run_time=2
      )
    )
    self.wait()

    for i in range(5):
      speedFactor = self.speedRamp(i)

      polychain = [
        Line(geneSegment[0] + coordZ, geneSegment[1] + coordZ, stroke_color=GREEN_C, stroke_width=70)
        for geneSegment in generationSegments[i]
      ]

      g = VGroup(*polychain)

      [self.play(Create(segment), run_time=0.5 * speedFactor) for segment in polychain]
      self.wait()

      self.play(FadeOut(g), run_time=1 * speedFactor)
      self.wait()

