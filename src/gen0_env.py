import pickle
from manim import *
from core.config import Config
from core.population import Population
from graphic.player import Player
from graphic.gene_g import GeneG


class Gen0Env:
  def __init__(
    self,
    populationFilename: str,
    configFilename: str,
    scaleK: float,
    iterationsNumber: int,
    tableRows: int,
    tableCols: int,
    player: Player,
    startEpoch: int,
    hideGenes: bool = False
  ):
    self.scaleK = scaleK
    self.iterationsNumber = iterationsNumber
    self.tableCols = tableCols
    self.tableRows = tableRows
    self.player = player

    with open(configFilename, "r") as f:
      Config.loadYaml(f)
    
    """
    Load population
    """
    with open(populationFilename, "rb") as f:
      self.pop: Population = pickle.load(f)
    
    """
    Problem constraints
    """
    self.outerCircle = Circle(radius = 33 * self.scaleK)
    self.innerCircle = Circle(radius = 2.5 * self.scaleK)
    self.innerCircle.shift((5.6 * self.scaleK, 0, 0))
    self.constraints = Cutout(
      self.outerCircle,
      self.innerCircle,
      fill_opacity = 0.5,
      color = BLUE,
      stroke_color = RED,
      stroke_width = 40 * self.scaleK
    )
    self.validTxt = Text("Valid?").scale(0.8).next_to(self.constraints, UP)
    self.geneIdTxt = Text("Gene ID: 0").scale(0.8).next_to(self.validTxt, UP)
    self.constraintsGroup = VGroup(self.constraints, self.geneIdTxt, self.validTxt)

    """
    Genes table
    """
    self.tableContent = [[
      VGroup(
        self.constraints.copy(),
        GeneG(self.pop.population[i + j * self.tableCols], 0).withScale(self.scaleK).withStrokeWidth(70).build() if not hideGenes else VMobject()
      )
      for i in range(self.tableCols)
    ] for j in range(self.tableRows)]

    self.table = MobjectTable(
      self.tableContent,
      include_outer_lines=True
    ).scale(0.12).to_edge(RIGHT)

    self.generationTxt = Text(f"Generation {startEpoch}").scale(0.8).next_to(self.table, UP)
    self.geneTableGroup = VGroup(self.generationTxt, self.table)


  def getEnvAsGroup(self) -> VGroup:
    ...
  
  def getCreationalAnimation(self) -> Animation:
    ...