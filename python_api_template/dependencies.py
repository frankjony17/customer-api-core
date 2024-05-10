from typing import Annotated

from fastapi import Depends, Security
from sqlalchemy.ext.asyncio import AsyncSession

from python_api_template.common.schemas.api_token import TokenModel
from python_api_template.internal.db.database import get_async_session
from python_api_template.internal.security import get_token_api_key

AsyncSessionDependency = Annotated[AsyncSession, Depends(get_async_session)]

TokenDependency = Annotated[TokenModel, Security(get_token_api_key)]
