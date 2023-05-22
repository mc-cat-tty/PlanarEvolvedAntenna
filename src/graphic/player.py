from manim import *
from os.path import join

class Player:  
  def __init__(self, width: float, height: float, controlsHeight: float = 0.5, startProgress: float = 0, startGen: int = 0, endGen: int = 1, trackText: str = "Intro"):
    self.width = width
    self.height = height
    self.progress = startProgress
    self.controlsHeight = controlsHeight
    self.stop = SVGMobject(file_name = join("..", "vectors", "stop.svg"), height = self.controlsHeight*1.5).to_edge(DOWN).shift((0, self.height*3, 0))
    self.play = SVGMobject(file_name = join("..", "vectors", "play.svg"), height = self.controlsHeight*1.5).to_edge(DOWN).shift((0, self.height*3, 0))
    self.pause = SVGMobject(file_name = join("..", "vectors", "pause.svg"), height = self.controlsHeight*1.5).to_edge(DOWN).shift((0, self.height*3, 0))
    self.fastForward = SVGMobject(file_name = join("..", "vectors", "fast_forward.svg"), height = self.controlsHeight*1.5).to_edge(DOWN).shift((0, self.height*3, 0))
    self.currentButton = self.stop
    self.backward = SVGMobject(file_name = join("..", "vectors", "backward.svg"), height = self.controlsHeight * 3/5).next_to(self.currentButton, LEFT, buff = MED_LARGE_BUFF).shift((0, self.height - self.controlsHeight * 3/5, 0))
    self.forward = SVGMobject(file_name = join("..", "vectors", "forward.svg"), height = self.controlsHeight * 3/5).next_to(self.currentButton, RIGHT, buff = MED_LARGE_BUFF).shift((0, self.height - self.controlsHeight * 3/5, 0))
    self.lastBuild = None
    self.animRunTime = 0.5
    self.startGen = startGen
    self.endGen = endGen
    self.trackText = Text(trackText, height = self.controlsHeight, font = "Inter", weight = SEMIBOLD)

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
  
  def toTrackText(self, txt: str) -> Animation:
    targetTxt = Text(txt, height = self.controlsHeight, font = "Inter", weight = SEMIBOLD).next_to(self.progressBarOutline, DOWN, buff = MED_SMALL_BUFF)
    return FadeTransform(self.trackText, targetTxt)
  
  def buildMobj(self) -> VGroup:
    self.progressBarOutline = RoundedRectangle(corner_radius = 0.08, height = self.height, width = self.width).next_to(self.currentButton, DOWN)
    self.progressBarFill = RoundedRectangle(
      corner_radius = 0.08,
      height = self.height,
      width = self.width * (self.progress + 1e-3),
      fill_color = GRAY,
      fill_opacity = 1,
      stroke_width = 0
    ).next_to(self.currentButton, DOWN).align_to(self.progressBarOutline, LEFT)
    self.startGenText = Text(f"Gen {self.startGen}", height = self.height, font = "Inter").next_to(self.progressBarOutline, LEFT)
    self.endGenText = Text(f"Gen {self.endGen}", height = self.height, font = "Inter").next_to(self.progressBarOutline, RIGHT)
    self.trackText = self.trackText.next_to(self.progressBarOutline, DOWN, buff = MED_SMALL_BUFF)
    g =  VGroup(self.currentButton, self.backward, self.forward, self.progressBarFill, self.progressBarOutline, self.startGenText, self.endGenText, self.trackText)
    self.lastBuild = g
    return g
  
  def toProgress(self, progress: float) -> Animation:
    self.progress = progress
    return Transform(self.lastBuild, self.buildMobj())
