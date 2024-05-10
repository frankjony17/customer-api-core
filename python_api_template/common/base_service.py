import copy
from typing import Any, Tuple, Type, TypeVar

from pydantic import BaseModel

from python_api_template.common.exceptions.exceptions import (
    NotFoundError,
)
from python_api_template.internal.decorators.decorator_metaclass import (
    DecoratorMetaclass,
)

T = TypeVar("T")


class BaseService(metaclass=DecoratorMetaclass):
    """
    BaseService class provides the base structure for service classes in your application.
    It has a class method 'query_result' which can be used to obtain the result of a query
    or raise an exception if the result is empty or null.
    """

    @staticmethod
    def query_result(
        result: list[Any] | dict[str, Any] | Type[BaseModel] | Tuple[Any] | None,
    ) -> Any:
        """
        This class method checks the result of a query and either returns the result or
        raises a 'NotFoundError'.

        The result can be of various types: a list, a dictionary, a BaseModel object or a tuple,
         and it can also be None.

        Args:
            result (Union[list[Any], dict[str, Any], Type[BaseModel], Optional[Tuple[Any]]]):
                The result of the query. This can be a list of items, a dictionary,
                 a BaseModel object, a tuple, or None.

        Returns:
            Any: A deep copy of the result of the query if it's not empty or None.

        Raises:
            NotFoundError: If the result is empty or None.
        """
        if result:
            return copy.deepcopy(result)
        raise NotFoundError
