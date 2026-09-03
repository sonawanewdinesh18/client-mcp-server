"""
Mathematics MCP Server (Built-in)
Provides comprehensive symbolic & numerical mathematics tools powered by SymPy and Python math.
"""
from mcp.server.fastmcp import FastMCP
import sympy as sp
import math
import json

mcp = FastMCP("Mathematics-Server")


@mcp.tool()
def calculate_expression(expression: str) -> str:
    """
    Evaluates a mathematical or algebraic expression symbolically or numerically.
    Examples: '2**10 + sqrt(144)', 'sin(pi/4) + cos(pi/4)', 'expand((x + 2)**3)'.
    """
    try:
        expr = sp.sympify(expression)
        simplified = sp.simplify(expr)
        numeric_val = expr.evalf() if expr.is_number else None
        
        result = {
            "expression": expression,
            "simplified": str(simplified),
            "latex": sp.latex(simplified)
        }
        if numeric_val is not None and not numeric_val.has(sp.I):
            result["numeric_approx"] = float(numeric_val)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error evaluating expression: {e}"

@mcp.tool()
def solve_equation(equation: str, variable: str = "x") -> str:
    """
    Solves algebraic equations symbolically.
    Examples: equation='x**2 - 5*x + 6 = 0', variable='x'.
    """
    try:
        var = sp.Symbol(variable)
        if "=" in equation:
            lhs, rhs = equation.split("=")
            eq = sp.Eq(sp.sympify(lhs), sp.sympify(rhs))
        else:
            eq = sp.sympify(equation)
            
        solutions = sp.solve(eq, var)
        return json.dumps({
            "equation": equation,
            "variable": variable,
            "solutions": [str(s) for s in solutions],
            "latex_solutions": [sp.latex(s) for s in solutions]
        }, indent=2)
    except Exception as e:
        return f"Error solving equation: {e}"

@mcp.tool()
def calculus_operation(expression: str, variable: str = "x", operation: str = "derivative") -> str:
    """
    Computes derivatives or integrals of mathematical functions.
    operation: 'derivative' | 'integral'
    Examples: expression='x**3 * sin(x)', variable='x', operation='derivative'.
    """
    try:
        var = sp.Symbol(variable)
        expr = sp.sympify(expression)
        
        if operation.lower() in ["derivative", "diff"]:
            res = sp.diff(expr, var)
            op_name = "Derivative"
        elif operation.lower() in ["integral", "integrate"]:
            res = sp.integrate(expr, var)
            op_name = "Indefinite Integral"
        else:
            return "Invalid operation. Choose 'derivative' or 'integral'."
            
        return json.dumps({
            "operation": op_name,
            "expression": expression,
            "variable": variable,
            "result": str(res),
            "latex": sp.latex(res)
        }, indent=2)
    except Exception as e:
        return f"Error performing calculus operation: {e}"

@mcp.tool()
def matrix_operations(matrix_data: list[list[float]], operation: str = "determinant") -> str:
    """
    Performs matrix operations: 'determinant', 'inverse', 'eigenvalues', 'rank', 'transpose'.
    matrix_data: 2D array of numbers, e.g. [[1, 2], [3, 4]]
    """
    try:
        M = sp.Matrix(matrix_data)
        op = operation.lower()
        
        if op == "determinant":
            val = M.det()
            res = {"determinant": float(val) if val.is_number else str(val)}
        elif op == "inverse":
            inv = M.inv()
            res = {"inverse": inv.tolist()}
        elif op == "eigenvalues":
            eigen = M.eigenvals()
            res = {"eigenvalues": {str(k): v for k, v in eigen.items()}}
        elif op == "transpose":
            res = {"transpose": M.T.tolist()}
        elif op == "rank":
            res = {"rank": M.rank()}
        else:
            return f"Unsupported operation '{operation}'. Use determinant, inverse, eigenvalues, transpose, or rank."
            
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Matrix error: {e}"

if __name__ == "__main__":
    mcp.run()
