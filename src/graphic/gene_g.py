import random
from manim import *
from core.gene import Gene

class GeneG:
  def __init__(self, gene: Gene, id: int):
    self.gene = gene
    self.id = id
  
  def withSpeedFactor(self, sf: float):
    self.speed_factor = sf
    return self
  
  def withScale(self, scale: float):
    self.scale = scale
    return self
  
  def withStrokeWidth(self, strokeWidth: float):
    self.strokeWidth = strokeWidth
    return self

  def build(self) -> VGroup:
    coordZ = (0,)
    generationSegments = [
      segment.toList()
      for segment in self.gene.getCartesianCoords()
    ]

    polychain = [
      Line(
        np.array(geneSegment[0] + coordZ) * self.scale,
        np.array(geneSegment[1] + coordZ) * self.scale,
        stroke_color = GREEN_C,
        stroke_width = self.strokeWidth * self.scale
      )
      for geneSegment in generationSegments
    ]

    self.polychain = VGroup(*polychain)
    return self.polychain
  
  def getCreateAnims(self, oldText: Text, id: int) -> Succession:
    """
    Warning: call this method always after build()
    """
    
    targetTxt = Text(f"Gene ID: {id}").scale(0.8).set_x(
      oldText.get_x()
    ).set_y(
      oldText.get_y()
    ).set_z(
      oldText.get_z()
    )
    animations: Succession = Succession(
      Transform(oldText, targetTxt, run_time=self.speed_factor),
      *[Create(segment, run_time=0.51 * random.random() * self.speed_factor) for segment in self.polychain],
    )

    return animations