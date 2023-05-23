from manim import *
from graphic.gene_g import GeneG
from graphic.loaders import loadPop
from typing import Dict
from rf.radiation import RadiationPattern, RpCardEvaluationInput
from rf.nec_analysis import NecAnalysis
from core.config import Config

def getAngleFromDict(d: Dict[float, Dict[float, float]], theta: float, phi: float) -> float:
  internalD = min(d.items(), key = lambda x: abs(phi - x[0]))[1]
  return min(internalD.items(), key = lambda x: abs(theta - x[0]))[1]

class RadiationPattern(ThreeDScene):
  def construct(self):
    """Plot radiation patter (3d, spherical coordinates)
    """
    EPOCH = 10
    GENE_IDX = 1
    SCALE_K = 1/30

    self.wait()

    axes = ThreeDAxes()
    labels = axes.get_axis_labels(
      Text("x gain [mW]").scale(0.6),
      Text("y gain [mW]").scale(0.6),
      Text("z gain [mW]").scale(0.6),
    )
    self.set_camera_orientation(phi = 0 * DEGREES, theta = 0 * DEGREES)

    with open("config.yaml", "r") as f:
      Config.loadYaml(f)
    
    pop = loadPop(EPOCH)
    gene = GeneG(pop.population[GENE_IDX], GENE_IDX)
    g = gene.withScale(SCALE_K).withStrokeWidth(70).build()
    outerCircle = Circle(radius = 33 * SCALE_K)
    innerCircle = Circle(radius = 2.5 * SCALE_K)
    innerCircle.shift((5.6 * SCALE_K, 0, 0))
    constraints = Cutout(
      outerCircle,
      innerCircle,
      fill_opacity = 0.2,
      color = RED,
      stroke_color = RED,
      stroke_width = 40 * SCALE_K
    ).shift((0, 0, -SCALE_K))



    gains = dict()
    with NecAnalysis(pop.population[GENE_IDX], 868e6) as sim:
      sim.addInfiniteGroundPlane()
      sim.runExcitation()
      for phi in range(0, 360, 3):
        rp = sim.computeRadiationPattern([
          RpCardEvaluationInput(90, 0, -3, phi, phi, 0, 0),  # sagittal plane (1)
          RpCardEvaluationInput(0, 90, 3, phi + 180, phi + 180, 0, 1)  # sagittal plane (2)
        ])

        gainsFixedPhi = dict(zip(rp.thetasRad, rp.gainsMw))
        gains[phi * PI / 180] = gainsFixedPhi

    s = Surface(
      lambda u, v: np.array([
        0.5 * getAngleFromDict(gains, u, v) * np.cos(u) * np.cos(v),
        0.5 * getAngleFromDict(gains, u, v) * np.cos(u) * np.sin(v),
        0.5 * getAngleFromDict(gains, u, v) * np.sin(u)
      ]),
      resolution = (30, 120),
      v_range = [0, TAU],
      u_range = [0, PI/2],
      fill_color = RED,
      fill_opacity = 0.5
    )

    fitnessText = Tex("$f = min(eval\_gains_{[30° < theta < 60°]})$").to_corner(DL)
    self.add_fixed_in_frame_mobjects(fitnessText)
    self.add_fixed_in_frame_mobjects(Text("Fitness evaluation").to_corner(UL))
    self.add_fixed_in_frame_mobjects(Text("868 MHz").to_corner(UR))

    self.play(
      Create(axes),
      Write(labels),
      Create(g),
      Create(constraints),
      Create(s)
    )
    
    self.wait()
    self.play(Transform(
      fitnessText,
      Tex(f"Fitness: {pop.population[GENE_IDX].fitness():.2}").to_corner(DL)
    ))

    self.begin_ambient_camera_rotation(rate = 0.2, about = "phi")
    self.wait()

    self.begin_ambient_camera_rotation(rate = 0.0001, about = "phi")
    self.begin_ambient_camera_rotation(rate = 1, about = "theta")
    self.wait(5)