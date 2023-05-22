from manim import *

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