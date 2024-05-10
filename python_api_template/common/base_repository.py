import uuid
from typing import Any, Generic, Type, TypeVar

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models.base_model import BaseOrmModel

T = TypeVar("T", bound=BaseOrmModel)


class BaseRepository(Generic[T]):
    """
    BaseRepository is a base class for repositories.

    A repository is an object that mediates between the domain and data mapping layers of
     an application. It's responsibility is to handle database operations.

    This base class has the following attributes:

    - `__abstract__`: A class attribute that suggests this class should not be
                     instantiated directly. In SQLAlchemy, this is often used for mixin or base
                     classes.
    - `async_session`: An instance of SQLAlchemy's AsyncSession class, used for interacting
                 with the database.

    This base class has the following methods:

    - `save`: Asynchronously saves a model instance to the database.
    """

    __abstract__ = True

    def __init__(self, async_session: AsyncSession):
        """
        Initializes the RepositoryBase instance.

        Args:
            async_session (AsyncSession):
            A SQLAlchemy session that will be used to query the database.
        """
        self.async_session = async_session

    async def save(self, model: T) -> T:
        """
        Asynchronously saves a model instance to the database.

        This method adds the model to the SQLAlchemy session, commits the session to save the model
        to the database, and refreshes the model to ensure it has the latest data from the database

        Args:
            model (Any): The model instance to be saved to the database.

        Returns:
            Any: The saved model instance, refreshed from the database.
        """
        self.async_session.add(model)
        await self.async_session.commit()
        await self.async_session.refresh(model)
        return model

    async def find_all(
        self,
        model: Type[T],
        skip: int = 0,
        limit: int = 100,
        options: list[Any] | None = None,
    ) -> list[T]:
        """
        Asynchronously finds all instances of a model, with optional pagination.

        Args:
            options:
            model (Type[Any]): The model class to query.
            skip (int, optional): Number of instances to skip for pagination. Defaults to 0.
            limit (int, optional): Maximum number of instances to return. Defaults to 100.

        Returns:
            list[Any]: A list of model instances.
        """

        stmt = select(model)
        if options is None:
            options = []
        stmt = stmt.options(*options)

        stmt = stmt.offset(skip).limit(limit)
        result = await self.async_session.execute(stmt)
        return list(result.scalars().all())

    async def find_one(
        self, model: Type[T], _id: uuid.UUID, options: list[Any] | None = None
    ) -> T:
        """
        Asynchronously finds a single instance of a model by its id.

        Args:
            options:
            model (Type[T]): The model class to query.
            _id (UUID): The id of the instance.

        Returns:
            T: The found instance.
            Throws an exception if the instance does not exist.
        """
        stmt = select(model)
        if options is None:
            options = []
        stmt = stmt.options(*options)
        stmt = stmt.where(model.id == _id)

        result = await self.async_session.execute(stmt)
        invoice = result.scalars().one()
        return invoice

    async def update(
        self,
        model: Type[T],
        _id: uuid.UUID,
        values: dict[str, Any],
        commit: bool = True,
    ) -> None:
        """
        Args:
            model: The type of the model to update.
            _id: The UUID of the object to update.
            values: A dictionary containing the updated values for the object.
            commit: A boolean indicating whether or not to commit the changes to the database.
                    Default is True.
        """
        stmt = update(model).where(model.id == _id).values(**values)
        await self.async_session.execute(stmt)
        if commit:
            await self.async_session.commit()

    async def delete(self, model: Type[T], _id: uuid.UUID) -> None:
        """
        Asynchronously deletes a model instance by its id.

        Args:
            model (Type[Any]): The model class to query.
            _id (UUID): The id of the instance to delete.

        Returns:
            None
        """
        stmt = delete(model).where(model.id == _id)

        async with self.async_session.begin():
            await self.async_session.execute(stmt)

    async def add(self, model: T) -> T:
        """
        Asynchronously adds a new instance to the session and flushes changes.

        Args:
            model (Any): The new instance to add.

        Returns:
            Any: The added instance with an id assigned.
        """
        self.async_session.add(model)
        await self.async_session.flush()
        return model

    async def add_all(self, models: list[T]) -> None:
        """
        Asynchronously adds a list of new instances to the session.

        Args:
            models (list[Any]): The new instances to add.

        Returns:
            None
        """
        self.async_session.add_all(models)
        await self.async_session.flush()
