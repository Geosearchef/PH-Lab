import math

def eval_expression(expr: str) -> str:
    return "Not available"

    # try:
    #     code = compile(expr, '<string>', 'eval')
    # except SyntaxError:
    #     return "Invalid expression."

    # allowed_names = { k: v for k, v in math.__dict__.items() if not k.startswith("__") }

    # for name in code.co_names:
    #     if name not in allowed_names:
    #         return f"Name '{name}' is not allowed."
    
    # try:
    #     result = str(eval(code, {"__builtins__": {}}, allowed_names))
    # except Exception as e:
    #     return "Error evaluating expression."

    # return result

