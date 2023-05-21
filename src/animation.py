import pickle
import random
import sys
from manim import *
from os.path import join
from typing import List, Tuple
from core.population import Population
from core.gene import Gene
from config import Config

OUTPUT_DIRECTORY = "results"
SCALE_K = 15

# Text.set_default(font = "Inter")

class Player:  
  def __init__(self, width: float, height: float, startProgress: float = 0, startGen: int = 0, endGen: int = 1):
    self.width = width
    self.height = height
    self.progress = startProgress
    self.stop = SVGMobject(file_name = join("..", "vectors", "stop.svg"), height = 0.5).to_edge(DOWN).shift((0, self.height , 0))
    self.play = SVGMobject(file_name = join("..", "vectors", "play.svg"), height = 0.5).to_edge(DOWN).shift((0, self.height , 0))
    self.pause = SVGMobject(file_name = join("..", "vectors", "pause.svg"), height = 0.5).to_edge(DOWN).shift((0, self.height , 0))
    self.fastForward = SVGMobject(file_name = join("..", "vectors", "fast_forward.svg"), height = 0.5).to_edge(DOWN).shift((0, self.height , 0))
    self.currentButton = self.stop
    self.lastBuild = None
    self.animRunTime = 0.5
    self.startGen = startGen
    self.endGen = endGen

  def withProgress(self, progress: float):
    self.progress = progress
    return self
  
  def updateButton(self, targetButton: SVGMobject) -> AnimationGroup:
    a = AnimationGroup(
      Indicate(targetButton, color = WHITE, scale_factor = 0.5),
      Indicate(self.currentButton, color = WHITE, scale_factor = 0.5),
      Transform(self.currentButton, targetButton),
      run_time = self.animRunTime
    )
    self.currentButton = self.stop
    return a

  def buttonToStop(self) -> AnimationGroup:
    return self.updateButton(self.stop)
    
  def buttonToPlay(self) -> AnimationGroup:
    return self.updateButton(self.play)
    
  def buttonToPause(self) -> AnimationGroup:
    return self.updateButton(self.pause)
    
  def buttonToFastForward(self) -> AnimationGroup:
    return self.updateButton(self.fastForward)
  
  def withStartGen(self, startGen: int):
    self.startGen
    return self
  
  def withEndGen(self, endGen: int):
    self.endGen = endGen
    return self
  
  def buildMobj(self) -> VGroup:
    progressBarOutline = RoundedRectangle(corner_radius = 0.08, height = self.height, width = self.width).next_to(self.currentButton, DOWN)
    progressBarFill = RoundedRectangle(
      corner_radius = 0.08,
      height = self.height,
      width = self.width * (self.progress + 1e-3),
      fill_color = GRAY,
      fill_opacity = 1,
      stroke_width = 0
    ).next_to(self.currentButton, DOWN).align_to(progressBarOutline, LEFT)
    startGenText = Text(f"Gen {self.startGen}", height = self.height).next_to(progressBarOutline, LEFT)
    endGenText = Text(f"Gen {self.endGen}", height = self.height).next_to(progressBarOutline, RIGHT)
    g =  VGroup(self.currentButton, progressBarFill, progressBarOutline, startGenText, endGenText)
    self.lastBuild = g
    return g
  
  def toProgress(self, progress: float) -> Animation:
    self.progress = progress
    return Transform(self.lastBuild, self.buildMobj())

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
        stroke_width=70/SCALE_K
      )
      for geneSegment in generationSegments
    ]

    animations: Succession = Succession(
      Transform(self.geneIdTxt, Text(f"Gene ID: {id}").to_corner(UL), run_time=speedFactor),
      *[Create(segment, run_time=0.51 * random.random() * speedFactor) for segment in polychain],
    )

    return VGroup(*polychain), animations


  def construct(self):
    with open("config.yaml", "r") as f:
      Config.loadYaml(f)

    epoch = 3
    geneId = 0
    itNum = 51
    self.geneIdTxt = Text(f"Gene ID: {geneId}").to_corner(UL)
    self.validTxt = Text("Valid?").next_to(self.geneIdTxt, DOWN)

    """
    Show player
    """
    player = Player(10, 0.2)
    self.add(player.buildMobj())

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

    self.play(player.buttonToPlay())

    """
    Load population and show some good gene generation
    """
    with open(join(OUTPUT_DIRECTORY, f"epoch_{epoch}.pkl"), "rb") as f:
      pop: Population = pickle.load(f)

    for i in range(geneId, 2):
      speedFactor = self.expSpeedRamp(i)

      g, createAnim = self.createGene(pop.population[i], geneId, speedFactor)

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
    return
    """
    Fast forward
    """
    for i in range(geneId, itNum):
      if geneId == 6: self.play(player.buttonToFastForward())

      speedFactor = -smooth(i*4 / itNum) + 1.1
      g, createAnim = self.createGene(pop.population[i], geneId, speedFactor)
      self.play(createAnim, player.toProgress((geneId + 1) / itNum), run_time = createAnim.run_time)
      
      self.play(
        Indicate(self.validTxt, color = GREEN, run_time = speedFactor),
        FadeOut(g, run_time = 0.7 * speedFactor)
      )

      self.wait(speedFactor)
      geneId += 1
    
