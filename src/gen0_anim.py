import pickle
from manim import *
from os.path import join
from typing import List
from core.config import Config
from core.population import Population
from core.gene import Gene
from graphic.player import Player
from graphic.gene_g import GeneG

OUTPUT_DIRECTORY = "results"
SCALE_K = 1 / 20


class Gen0(MovingCameraScene):
  def expSpeedRamp(self, x: float) -> float:
    center = 1
    plateau = 0.3
    scaleY = 3
    return np.exp(- (x - center)) / scaleY + plateau

  def construct(self):
    with open("config.yaml", "r") as f:
      Config.loadYaml(f)

    epoch = 3
    geneId = 0
    itNum = 61

    """
    Show player
    """
    player = Player(10, 0.2, 0.3, trackText="Problem's space constraints")
    self.add(player.buildMobj())

    """
    Show problem constraints
    """
    outerCircle = Circle(radius = 33 * SCALE_K)
    innerCircle = Circle(radius = 2.5 * SCALE_K)
    innerCircle.shift((5.6 * SCALE_K, 0, 0))
    self.constraints = Cutout(
      outerCircle,
      innerCircle,
      fill_opacity = 0.5,
      color = BLUE,
      stroke_color = RED,
      stroke_width = 40 * SCALE_K
    )

    self.validTxt = Text("Valid?").scale(0.8).next_to(self.constraints, UP)
    self.geneIdTxt = Text(f"Gene ID: {geneId}").scale(0.8).next_to(self.validTxt, UP)
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

    self.play(
      player.buttonToPause(),
      player.toTrackText("Genes random generation")
    )

    """
    Load population and show some good gene generation
    """
    with open(join(OUTPUT_DIRECTORY, f"epoch_{epoch}.pkl"), "rb") as f:
      pop: Population = pickle.load(f)
    
    cols = 8
    rows = 8
    tableCreated = False
    content = [[self.constraints.copy() for _ in range(cols)] for _ in range(rows)]

    for i in range(geneId, 3):
      if geneId == 2:
        geneTable = MobjectTable(
          content,
          include_outer_lines=True
        ).scale(0.12).to_edge(RIGHT)
        generationTxt = Text(f"Generation {epoch}").scale(0.8).next_to(geneTable, UP)
        geneTableGroup = VGroup(generationTxt, geneTable)
        self.play(
          Create(geneTable),
          Create(generationTxt),
          constraintsGroup.animate.to_edge(LEFT)
        )
        
        tableCreated = True
      
      speedFactor = self.expSpeedRamp(i)

      gene = GeneG(pop.population[i], geneId)
      g = gene.withScale(SCALE_K).withStrokeWidth(70).build()
      createAnim = gene.withSpeedFactor(speedFactor).getCreateAnims(self.geneIdTxt, geneId)
      if tableCreated: g.to_edge(LEFT)

      self.play(createAnim, player.toProgress(geneId / itNum))

      miniatureShift = - (outerCircle.width - g.width) * 0.12 / 2
      if not tableCreated:
        self.play(
          Indicate(self.validTxt, color=GREEN),
          FadeOut(g)
        )
        [line.set_stroke(width = 70 * SCALE_K * 0.12 * 2) for line in g]
        content[geneId // cols][geneId % cols].add(g)
        
      else:
        g.generate_target()
        [line.set_stroke(width = 70 * SCALE_K * 0.12 * 2) for line in g.target]
        g.target.move_to(
          geneTable.get_cell((
            geneId // cols + 1,
            geneId % cols + 1
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
    with open(join(OUTPUT_DIRECTORY, f"invalids.pkl"), "rb") as f:
      invalids: List[Gene] = pickle.load(f)
    
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
      g = gene.withScale(SCALE_K).withStrokeWidth(70).build()
      createAnim = gene.withSpeedFactor(speedFactor).getCreateAnims(self.geneIdTxt, geneId)
      g.to_edge(LEFT)
      self.play(createAnim, player.toProgress(geneId / itNum))

      t = Text(txt, color = RED).next_to(self.constraints, RIGHT)
      self.play(
        Succession(
          *[FadeToColor(g, color = RED if i%2 == 0 else GREEN, run_time=0.3) for i in range(5)]
        ),
        Create(t)
      )
      
      highlight = geneTable.get_highlighted_cell((
          geneId // cols + 1,
          geneId % cols + 1
      ), color = RED)
      geneTable.add_to_back(highlight)

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
      player.buttonToPlay()
    )
    self.play(
      self.camera.frame.animate.scale(0.2)
    )
    self.wait()
    self.play(
      self.camera.frame.animate.scale(5)
    )
    self.play(
      player.buttonToPause()
    )

    """
    Fast forward
    """
    for i in range(geneId, itNum):
      if geneId == 8: self.play(player.showFastForward()); return

      """Generate gene
      """
      speedFactor = -smooth(i*4 / itNum) + 1.1
      gene = GeneG(pop.population[i], geneId)
      g = gene.withScale(SCALE_K).withStrokeWidth(70).build()
      createAnim = gene.withSpeedFactor(speedFactor).getCreateAnims(self.geneIdTxt, geneId)
      g.to_edge(LEFT)
      
      """Move gene to table
      """
      miniatureShift = - (outerCircle.width - g.width) * 0.12 / 2
      g.generate_target()
      [line.set_stroke(width = 70 * SCALE_K * 0.12 * 2) for line in g.target]
      g.target.move_to(
        geneTable.get_cell((
          geneId // cols + 1,
          geneId % cols + 1
        )).get_center_of_mass()
      ).shift((miniatureShift, 0, 0)).scale(0.12)

      self.play(
        # Indicate(self.validTxt, color = GREEN, run_time = speedFactor),
        MoveToTarget(g, run_time = 1.5 * speedFactor)
      )

      self.wait(speedFactor)
      geneId += 1
    
