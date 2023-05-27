import pickle
from manim import *
from os.path import join
from core.config import Config
from gen0_env import Gen0Env
from graphic.gene_g import GeneG
from graphic.player import Player

EPOCH = 3

class Niching(MovingCameraScene, Gen0Env):
  def construct(self):
    Gen0Env.__init__(
      self,
      populationFilename = join("results", f"epoch_{EPOCH}.pkl"),
      configFilename = "config.yaml",
      scaleK = 1 / 20,
      iterationsNumber = 61,
      tableRows = 8,
      tableCols = 8,
      startEpoch = EPOCH,
      player = Player(10, 0.2, 0.3, targetProgress = 66, startProgress = 61, trackText="Genes random generation")
    )

    self.add(
      self.table,
      self.player.withPauseButton().buildMobj()
    )

    self.play(self.player.toTrackText("Crossover"))

