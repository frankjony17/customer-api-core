from typing import Any


def format_func_and_args_name(func, args) -> tuple[str, Any]:
    name = func.__name__
    if args and hasattr(args[0], name):
        func_name = f"{args[0].__class__.__name__}.{name}"
    else:
        func_name = name
    args_repr = [
        f"{a.__class__.__name__}" if i == 0 and hasattr(a, "__class__") else repr(a)
        for i, a in enumerate(args)
    ]
    return func_name, args_repr
