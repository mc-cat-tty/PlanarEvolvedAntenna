from manim import *
from os.path import join

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
      Transform(self.currentButton, targetButton),
      run_time = self.animRunTime
    )
    self.currentButton = targetButton
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
