import inspect
from typing import Callable, Awaitable, Any, TypeVar

from python_api_template.common.exceptions.exceptions import InternalServerError
from .format_func_and_args_name import format_func_and_args_name

T = TypeVar("T")


async def bind_arguments(
    func: Callable[..., Awaitable[T]], *args: Any, **kwargs: Any
) -> dict[str, Any]:
    """
    Bind arguments to a function's signature, apply defaults, and raise a detailed error.

    This function is useful for debugging and error handling in cases where it's
    critical to understand the complete set of arguments that led to an error.

    Args:
        func (Callable): The function whose parameters to bind.
        *args: Positional arguments passed to the function.
        **kwargs: Keyword arguments passed to the function.

    Raises:
        InternalServerError: If there is a mismatch in the number of positional arguments or an argument is passed that doesn't correspond to any function parameter.

    Returns:
        dict[str, Any]: A dictionary of the bound arguments, including defaults.
    """

    func_name, args_repr = format_func_and_args_name(func, args)
    try:
        # Get the signature of the function.
        signature = inspect.signature(func)

        # Bind the provided arguments to the parameters in the function signature.
        # This will raise a TypeError if there are missing required arguments
        # or an excess of positional arguments.
        bound_args = signature.bind(*args_repr, **kwargs)

        # Apply default values to any parameters that were not provided in the call.
        bound_args.apply_defaults()

    except TypeError as exc:
        error_message = (
            f"Error in binding arguments to function '{func_name}': {str(exc)}"
        )
        raise InternalServerError(detail=error_message)

    # Return the full dictionary of arguments, including defaults applied.
    return bound_args.arguments


if __name__ == "__main__":
    import asyncio

    async def main():
        def some_function(a, b, c=3):
            pass

        result = await bind_arguments(some_function, 2, 3, d=4)
        # output: InternalServerError: 500: Error in binding arguments to
        # function 'some_function': got an unexpected keyword argument 'd'

        print(result)

    asyncio.run(main())
