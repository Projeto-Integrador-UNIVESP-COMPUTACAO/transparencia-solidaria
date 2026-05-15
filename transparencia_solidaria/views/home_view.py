from fastapi import Depends
from fastapi.requests import Request
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from transparencia_solidaria.core.configs import settings
from transparencia_solidaria.core.database import get_session
from transparencia_solidaria.repositories.estoque_repository import get_entidade_mais_critica


router = APIRouter()


# @router.get('/', name='index')
# async def index(request: Request):
#     context = {'request': request}
#     return settings.TEMPLATES.TemplateResponse(name='index.html', **context)

@router.get('/', name='index')
async def index(request: Request, db: AsyncSession = Depends(get_session)):
    entidade, itens_criticos = await get_entidade_mais_critica(db)

    context = {
        'entidade_destaque': entidade,
        'itens_criticos': itens_criticos,
    }
    return settings.TEMPLATES.TemplateResponse(name='index.html', request=request, context=context)


@router.get('/entidade', name='entidade')
async def index(request: Request):
    context = {'request': request}
    return settings.TEMPLATES.TemplateResponse(name='entidade.html', **context)
