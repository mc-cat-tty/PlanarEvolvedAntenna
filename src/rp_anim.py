from manim import *
from graphic.gene_g import GeneG
from graphic.loaders import loadPop
from rf.radiation import RadiationPattern, RpCardEvaluationInput
from rf.nec_analysis import NecAnalysis

class RadiationPattern(ThreeDScene):
  def construct(self):
    """Plot radiation patter (3d, spherical coordinates)
    """
    axes = ThreeDAxes()
    labels = axes.get_axis_labels(
      Text("x gain [mW]"),
      Text("y gain [mW]"),
      Text("z gain [mW]"),
    )
    self.set_camera_orientation(phi = 45 * DEGREES, theta = 0 * DEGREES)
    
    SCALE_K = 1/10
    GENE_IDX = 1
    pop = loadPop(3)
    gene = GeneG(pop.population[GENE_IDX], GENE_IDX)
    g = gene.withScale(SCALE_K).withStrokeWidth(70).build()
    outerCircle = Circle(radius = 33 * SCALE_K)
    innerCircle = Circle(radius = 2.5 * SCALE_K)
    innerCircle.shift((5.6 * SCALE_K, 0, 0))
    constraints = Cutout(
      outerCircle,
      innerCircle,
      fill_opacity = 0.2,
      color = BLUE,
      stroke_color = BLUE,
      stroke_width = 40 * SCALE_K
    ).shift((0, 0, -SCALE_K))

    # self.play(
    #   Create(axes),
    #   Write(labels),
    #   Create(g),
    #   Create(constraints)
    # )
    # self.wait()
    self.add(axes, labels, g, constraints)

    with NecAnalysis(pop.population[GENE_IDX], 868e6) as sim:
      sim.addInfiniteGroundPlane()
      sim.runExcitation()
      rp = sim.computeRadiationPattern([
        RpCardEvaluationInput(90, 0, -3, 45, 45, 0, 0),  # sagittal plane (1)
        RpCardEvaluationInput(15, 90, 3, 225, 225, 0, 1)  # sagittal plane (2)
      ])

    gains = dict(zip(rp.thetasRad, rp.gainsMw))

    s = Surface(
      lambda u, v: np.array([
        min(gains.items(), key = lambda x: abs(u - x[0]))[1] * np.cos(u) * np.cos(v),
        min(gains.items(), key = lambda x: abs(u - x[0]))[1] * np.cos(u) * np.sin(v),
        min(gains.items(), key = lambda x: abs(u - x[0]))[1] * np.sin(u)
      ]),
      resolution = (3, 360),
      v_range = [0, TAU],
      u_range = [0 * DEGREES, 90 * DEGREES],
      checkerboard_colors = [RED]
    )
    self.add(s); return

    self.begin_ambient_camera_rotation(rate = 1, about = "phi")
    self.wait()

    self.begin_ambient_camera_rotation(rate = 0.2, about = "theta")
    self.wait()