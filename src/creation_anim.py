import pickle
from manim import *
from os.path import join
from typing import List
from core.config import Config
from core.population import Population
from core.gene import Gene
from gen0_env import Gen0Env
from graphic.player import Player
from graphic.gene_g import GeneG

EPOCH = 3

class Creation(MovingCameraScene, Gen0Env):
  def __init__(self):
    Gen0Env.__init__(
      self,
      populationFilename = join("results", f"epoch_{EPOCH}.pkl"),
      configFilename = "config.yaml",
      scaleK = 1 / 20,
      tableRows = 8,
      tableCols = 8,
      startEpoch = EPOCH,
      player = Player(10, 0.2, 0.3, targetProgress = 66, startProgress = 0, trackText="Problem's space constraints"),
      hideGenes = True
    )
    MovingCameraScene.__init__(self)
  
  def expSpeedRamp(self, x: float) -> float:
    center = 1
    plateau = 0.3
    scaleY = 3
    return np.exp(- (x - center)) / scaleY + plateau

  def construct(self):
    geneId = 0

    self.add(self.player.buildMobj())

    """
    Show problem constraints
    """
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

    self.play(
      self.player.buttonToPause(),
      self.player.toTrackText("Genes random generation")
    )
    

    tableCreated = False
    for i in range(geneId, 3):
      if geneId == 2:
        self.play(
          Create(self.table),
          Create(self.generationTxt),
          self.constraintsGroup.animate.to_edge(LEFT)
        )
        
        tableCreated = True
      
      speedFactor = self.expSpeedRamp(i)

      gene = GeneG(self.pop.population[i], geneId)
      g = gene.withScale(self.scaleK).withStrokeWidth(70).build()
      createAnim = gene.withSpeedFactor(speedFactor).getCreateAnims(self.geneIdTxt, geneId)

      if tableCreated: g.to_edge(LEFT)

      self.play(createAnim, self.player.toProgress(geneId))

      miniatureShift = - (self.outerCircle.width - g.width) * 0.12 / 2
      if not tableCreated:
        self.play(
          Indicate(self.validTxt, color=GREEN),
          FadeOut(g)
        )
        [line.set_stroke(width = 70 * self.scaleK * 0.12 * 2) for line in g]
        g.move_to(
          self.table.get_cell((
            geneId // self.tableCols + 1,
            geneId % self.tableCols + 1
          )).get_center_of_mass()
        ).shift((miniatureShift, 0, 0)).scale(0.12)
        self.tableContent[geneId // self.tableCols][geneId % self.tableCols].add(g)
        
      else:
        g.generate_target()
        [line.set_stroke(width = 70 * self.scaleK * 0.12 * 2) for line in g.target]
        g.target.move_to(
          self.table.get_cell((
            geneId // self.tableCols + 1,
            geneId % self.tableCols + 1
          )).get_center_of_mass()
        ).shift((miniatureShift, 0, 0)).scale(0.12)

        self.play(
          Indicate(self.validTxt, color=GREEN),
          MoveToTarget(g)
        )

        
      self.wait(0.5)
      geneId += 1

    
    """
    Load wrong genes and show their generation and denstruction
    """
    with open(join("results", f"invalids.pkl"), "rb") as outFile:
      invalids: List[Gene] = pickle.load(outFile)
    
    invalidIdxs = [
      0,  # Circle breaker
      94,  # Inner hole intersecter
      30  # Self intersecter
    ]
    invalidTxt = [
      "Overflow",
      "Hole-intersecting",
      "Self-intersecting"
    ]
    for idx, txt in zip(invalidIdxs, invalidTxt):
      gene = GeneG(invalids[idx], geneId)
      g = gene.withScale(self.scaleK).withStrokeWidth(70).build()
      createAnim = gene.withSpeedFactor(speedFactor).getCreateAnims(self.geneIdTxt, geneId)
      g.to_edge(LEFT)
      self.play(createAnim, self.player.toProgress(geneId))

      t = Text(txt, color = RED).next_to(self.constraints, RIGHT)
      self.play(
        Succession(
          *[FadeToColor(g, color = RED if i%2 == 0 else GREEN, run_time=0.3) for i in range(5)]
        ),
        Create(t)
      )
      
      highlight = self.table.get_highlighted_cell((
          geneId // self.tableCols + 1,
          geneId % self.tableCols + 1
      ), color = RED)
      self.table.add_to_back(highlight)

      self.play(
        Succession(
          FadeToColor(self.validTxt, color = RED),
          FadeToColor(self.validTxt, color = WHITE, run_time = 0.5)
        ),
        Wiggle(self.validTxt),
        Uncreate(g),
        Uncreate(t)
      )
      self.wait(0.5)

      geneId += 1
    
    
    self.play(Transform(
      self.validTxt,
      Text("Fitness: xx.xx").scale(0.8).next_to(self.constraints, UP)
    ))
    self.wait()

    """
    Show radiation pattern (another, external, scene)
    """
    self.play(
      self.player.buttonToPlay()
    )
    self.play(
      self.camera.frame.animate.scale(0.2)
    )
    self.wait()
    self.play(
      self.camera.frame.animate.scale(5)
    )
    self.play(
      self.player.buttonToPause()
    )

    """
    Fast forward
    """
    for i in range(geneId, self.iterationsNumber):
      if geneId == 8: self.play(self.player.showFastForward())

      """
      Generate gene
      """
      speedFactor = -smooth(i*4 / self.iterationsNumber) + 1.1
      gene = GeneG(self.pop.population[i], geneId)
      g = gene.withScale(self.scaleK).withStrokeWidth(70).build()
      createAnim = gene.withSpeedFactor(speedFactor).getCreateAnims(self.geneIdTxt, geneId)
      g.to_edge(LEFT)
      self.play(createAnim, self.player.toProgress(geneId))
      
      """
      Move gene to table
      """
      miniatureShift = - (self.outerCircle.width - g.width) * 0.12 / 2
      g.generate_target()
      [line.set_stroke(width = 70 * self.scaleK * 0.12 * 2) for line in g.target]
      g.target.move_to(
        self.table.get_cell((
          geneId // self.tableCols + 1,
          geneId % self.tableCols + 1
        )).get_center_of_mass()
      ).shift((miniatureShift, 0, 0)).scale(0.12)

      print(geneId // self.tableCols, geneId % self.tableCols)

      self.play(
        # Indicate(self.validTxt, color = GREEN, run_time = speedFactor),
        MoveToTarget(g, run_time = 1.5 * speedFactor)
      )

      self.wait(speedFactor)
      geneId += 1