import pickle
import random
from manim import *
from os.path import join
from typing import List, Tuple
from config import Config
from graphic.player import Player
from core.population import Population
from core.gene import Gene

OUTPUT_DIRECTORY = "results"
SCALE_K = 15

# Text.set_default(font = "Inter")

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

class RodIncrementalGene(MovingCameraScene):
  def expSpeedRamp(self, x: float) -> float:
    center = 1
    plateau = 0.3
    scaleY = 3
    return np.exp(- (x - center)) / scaleY + plateau

  def createGene(self, gene: Gene, id: int, speedFactor) -> Tuple[VGroup, Succession]:
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
        stroke_width=70 / SCALE_K
      )
      for geneSegment in generationSegments
    ]

    targetTxt = self.geneIdTxt.copy()
    targetTxt.text = f"Gene ID: {id}"
    animations: Succession = Succession(
      Transform(self.geneIdTxt, targetTxt, run_time=speedFactor),
      *[Create(segment, run_time=0.51 * random.random() * speedFactor) for segment in polychain],
    )

    return VGroup(*polychain), animations


  def construct(self):
    with open("config.yaml", "r") as f:
      Config.loadYaml(f)

    epoch = 3
    geneId = 0
    itNum = 51

    """
    Show player
    """
    player = Player(10, 0.2)
    self.add(player.buildMobj())

    """
    Show problem constraints
    """
    outerCircle = Circle(radius = 33/SCALE_K)
    innerCircle = Circle(radius = 2.5/SCALE_K)
    innerCircle.shift((5.6 / SCALE_K, 0, 0))
    self.constraints = Cutout(
      outerCircle,
      innerCircle,
      fill_opacity = 0.5,
      color = BLUE,
      stroke_color = RED,
      stroke_width = 40/SCALE_K
    )

    self.validTxt = Text("Valid?", font_size = DEFAULT_FONT_SIZE*0.8).next_to(self.constraints, UP)
    self.geneIdTxt = Text(f"Gene ID: {geneId}", font_size = DEFAULT_FONT_SIZE*0.8).next_to(self.validTxt, UP)
    constraintsGroup = VGroup(self.constraints, self.geneIdTxt, self.validTxt)
    self.play(
      Write(
        self.constraints,
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

    self.play(player.buttonToPlay())

    """
    Load population and show some good gene generation
    """
    with open(join(OUTPUT_DIRECTORY, f"epoch_{epoch}.pkl"), "rb") as f:
      pop: Population = pickle.load(f)

    polychainToLeft = False
    for i in range(geneId, 3):
      if geneId == 2:
        content = [[self.constraints.copy() for _ in range(8)] for _ in range(9)]
        self.play(
          Create(
            MobjectTable(
              content
            ).scale(0.12).to_edge(RIGHT)
          ),
          constraintsGroup.animate.to_edge(LEFT)
        )
        
        polychainToLeft = True
      
      speedFactor = self.expSpeedRamp(i)

      g, createAnim = self.createGene(pop.population[i], geneId, speedFactor)
      if polychainToLeft: g.to_edge(LEFT)

      self.play(createAnim, player.toProgress(geneId / itNum))

      self.play(
        Indicate(self.validTxt, color=GREEN),
        FadeOut(g)
      )
      self.wait(0.5)
      geneId += 1
    
    """
    Load wrong genes and show their generation and denstruction
    """
    with open(join(OUTPUT_DIRECTORY, f"invalids.pkl"), "rb") as f:
      invalids: List[Gene] = pickle.load(f)
    
    invalidIdxs = [
      0,  # Circle breaker
      94,  # Inner hole intersecter
      30  # Self intersecter
    ]
    for idx in invalidIdxs:
      g, createAnim = self.createGene(invalids[idx], geneId, 0.5)
      g.to_edge(LEFT)
      self.play(createAnim, player.toProgress(geneId / itNum))
      self.play(
        Succession(
          *[FadeToColor(g, color = RED if i%2 == 0 else GREEN, run_time=0.3) for i in range(5)]
        )
      )
      self.play(
        Succession(
          FadeToColor(self.validTxt, color = RED),
          FadeToColor(self.validTxt, color = WHITE, run_time = 0.5)
        ),
        Wiggle(self.validTxt),
        Uncreate(g)
      )
      self.wait(0.5)

      geneId += 1
    
    """
    Fast forward
    """
    for i in range(geneId, itNum):
      if geneId == 6: self.play(player.buttonToFastForward()); return

      speedFactor = -smooth(i*4 / itNum) + 1.1
      g, createAnim = self.createGene(pop.population[i], geneId, speedFactor)
      g.to_edge(LEFT)
      self.play(createAnim, player.toProgress((geneId + 1) / itNum), run_time = createAnim.run_time)
      
      self.play(
        Indicate(self.validTxt, color = GREEN, run_time = speedFactor),
        FadeOut(g, run_time = 0.7 * speedFactor)
      )

      self.wait(speedFactor)
      geneId += 1
    
