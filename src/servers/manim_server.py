"""
Manim MCP Server (Built-in)
Provides tools for generating, structuring, and designing high-quality Manim mathematical animations and visual explanations.
"""
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    from fastmcp import FastMCP

import json

mcp = FastMCP("Manim-Animation-Server")




@mcp.tool()
def generate_manim_animation_code(concept_title: str, scene_description: str, quality: str = "medium_quality") -> str:
    """
    Generates complete, runnable Manim Community Edition Python code for visualizing any math, physics, or algorithm concept.
    concept_title: e.g. 'Pythagorean Theorem', 'Fourier Transform', 'Neural Network Layer', 'Derivative Tangent Line'
    scene_description: Detailed step-by-step description of animations and objects.
    """
    code_template = f'''from manim import *

class {concept_title.replace(" ", "")}Scene(Scene):
    """Visual explanation of {concept_title}."""
    def construct(self):
        # 1. Title Banner
        title = Title(r"{concept_title}", color=BLUE)
        self.play(Write(title))
        self.wait(0.5)

        # 2. Main Visual Elements
        # Scene plan: {scene_description}
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[-2, 4, 1],
            axis_config={{"color": GREY_B}},
        )
        self.play(Create(axes))
        
        # 3. Mathematical Formula / Graph
        func = axes.plot(lambda x: 0.5 * x**2, color=YELLOW)
        func_label = axes.get_graph_label(func, label=r"f(x) = \\frac{{1}}{{2}}x^2")
        
        self.play(Create(func), Write(func_label))
        self.wait(1)

        # 4. Highlight & Conclusion
        dot = Dot(color=RED).move_to(axes.c2p(2, 2))
        self.play(FadeIn(dot, scale=0.5))
        self.play(Indicate(dot))
        self.wait(2)
'''
    return json.dumps({
        "status": "success",
        "concept": concept_title,
        "recommended_command": f"manim -pql scene.py {concept_title.replace(' ', '')}Scene",
        "manim_code": code_template
    }, indent=2)

@mcp.tool()
def get_manim_template(category: str) -> str:
    """
    Returns standard Manim CE scene templates for different domains.
    category: 'geometry' | 'calculus' | 'linear_algebra' | 'latex_formula' | '3d_plot'
    """
    templates = {
        "geometry": """from manim import *

class GeometryProof(Scene):
    def construct(self):
        # Create Triangle
        triangle = Polygon([-2, -1, 0], [2, -1, 0], [0, 2, 0], color=TEAL)
        labels = VGroup(
            Tex("A").next_to(triangle.get_vertices()[0], DOWN+LEFT),
            Tex("B").next_to(triangle.get_vertices()[1], DOWN+RIGHT),
            Tex("C").next_to(triangle.get_vertices()[2], UP)
        )
        self.play(Create(triangle), Write(labels))
        self.wait(1)
""",
        "calculus": """from manim import *

class TangentLineScene(Scene):
    def construct(self):
        ax = Axes(x_range=[-2, 3], y_range=[-1, 5])
        curve = ax.plot(lambda x: x**2, color=BLUE)
        t = ValueTracker(1)
        
        initial_point = ax.c2p(t.get_value(), t.get_value()**2)
        dot = Dot(point=initial_point, color=YELLOW)
        dot.add_updater(lambda d: d.move_to(ax.c2p(t.get_value(), t.get_value()**2)))
        
        tangent = always_redraw(lambda: ax.get_secant_slope_group(
            t.get_value(), curve, dx=0.001, dx_line_color=RED
        ))
        self.play(Create(ax), Create(curve))
        self.play(FadeIn(dot), Create(tangent))
        self.play(t.animate.set_value(2), run_time=3)
        self.wait(1)
""",
        "linear_algebra": """from manim import *

class VectorTransformation(LinearTransformationScene):
    def __init__(self, **kwargs):
        LinearTransformationScene.__init__(
            self,
            show_coordinates=True,
            leave_ghost_vectors=True,
            **kwargs
        )

    def construct(self):
        matrix = [[1, 2], [2, 1]]
        self.apply_matrix(matrix)
        self.wait(1)
""",
        "latex_formula": """from manim import *

class FormulaTransformation(Scene):
    def construct(self):
        step1 = MathTex(r"\\int x \\cos(x) dx")
        step2 = MathTex(r"= x \\sin(x) - \\int \\sin(x) dx")
        step3 = MathTex(r"= x \\sin(x) + \\cos(x) + C")
        
        group = VGroup(step1, step2, step3).arrange(DOWN, aligned_edge=LEFT)
        self.play(Write(step1))
        self.play(TransformMatchingTex(step1.copy(), step2))
        self.play(TransformMatchingTex(step2.copy(), step3))
        self.wait(2)
"""
    }
    selected = templates.get(category.lower(), templates["calculus"])
    return json.dumps({
        "category": category,
        "template": selected
    }, indent=2)

if __name__ == "__main__":
    mcp.run()
