from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from transparencia_solidaria.models.estoque_model import Entidade, ItemEstoque, Cidade


async def buscar_itens(
    db: AsyncSession,
    categoria: str | None = None,
    entidade_id: int | None = None,
    skip: int = 0,
    limit: int = 20,
):
    stmt = (
        select(ItemEstoque)
        .options(selectinload(ItemEstoque.entidade))
        .order_by(ItemEstoque.id.desc())
    )

    if categoria:
        stmt = stmt.where(ItemEstoque.categoria == categoria)

    if entidade_id:
        stmt = stmt.where(ItemEstoque.entidade_id == entidade_id)

    stmt = stmt.offset(skip).limit(limit)

    result = await db.execute(stmt)
    return result.scalars().all()


async def listar_categorias(db: AsyncSession):
    stmt = (
        select(ItemEstoque.categoria).distinct().order_by(ItemEstoque.categoria.asc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def listar_entidades(db: AsyncSession, categoria: str | None = None):
    stmt = select(Entidade).join(ItemEstoque, ItemEstoque.entidade_id == Entidade.id)

    if categoria:
        stmt = stmt.where(ItemEstoque.categoria == categoria)

    stmt = stmt.distinct().order_by(Entidade.nome.asc())

    result = await db.execute(stmt)
    return result.scalars().all()


async def buscar_entidade_por_id(db: AsyncSession, entidade_id: int):
    stmt = select(Entidade).where(Entidade.id == entidade_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def buscar_itens(
    db: AsyncSession,
    categoria: str | None = None,
    entidade_id: int | None = None,
    ordenar_por: str = "id",
    ordem: str = "desc",
    skip: int = 0,
    limit: int = 20,
):
    status_ordenacao = case(
        (ItemEstoque.quantidade_atual <= 0, 0),
        (ItemEstoque.quantidade_atual < ItemEstoque.quantidade_necessaria, 1),
        else_=2,
    )

    colunas_ordenacao = {
        "id": ItemEstoque.id,
        "produto": ItemEstoque.produto,
        "categoria": ItemEstoque.categoria,
        "quantidade_atual": ItemEstoque.quantidade_atual,
        "quantidade_necessaria": ItemEstoque.quantidade_necessaria,
        "unidade": ItemEstoque.unidade,
        "atualizado_em": ItemEstoque.atualizado_em,
        "entidade": Entidade.nome,
        "status": status_ordenacao,
    }

    coluna = colunas_ordenacao.get(ordenar_por, ItemEstoque.id)

    stmt = (
        select(ItemEstoque)
        .join(Entidade, ItemEstoque.entidade_id == Entidade.id)
        .options(selectinload(ItemEstoque.entidade))
    )

    if categoria:
        stmt = stmt.where(ItemEstoque.categoria == categoria)

    if entidade_id:
        stmt = stmt.where(ItemEstoque.entidade_id == entidade_id)

    if ordem == "asc":
        stmt = stmt.order_by(coluna.asc())
    else:
        stmt = stmt.order_by(coluna.desc())

    stmt = stmt.offset(skip).limit(limit)

    result = await db.execute(stmt)
    return result.scalars().all()


async def get_entidade_mais_critica(db: AsyncSession):
    percentual = case(
        (ItemEstoque.quantidade_necessaria == 0, 100.0),
        else_=(ItemEstoque.quantidade_atual / ItemEstoque.quantidade_necessaria * 100),
    )

    # Subquery: entidade com mais itens críticos
    subq = (
        select(ItemEstoque.entidade_id, func.count().label("qtd_criticos"))
        .where(percentual < 25)
        .group_by(ItemEstoque.entidade_id)
        .order_by(func.count().desc())
        .limit(1)
        .subquery()
    )

    # Busca a entidade já carregando cidade e cidade.estado
    stmt_entidade = (
        select(Entidade)
        .join(subq, Entidade.id == subq.c.entidade_id)
        .options(selectinload(Entidade.cidade).selectinload(Cidade.estado))
    )
    result = await db.execute(stmt_entidade)
    entidade = result.scalars().first()

    if not entidade:
        return None, []

    # Busca os 3 itens mais críticos dessa entidade
    stmt_itens = (
        select(ItemEstoque)
        .where(ItemEstoque.entidade_id == entidade.id)
        .order_by(percentual.asc())
        .limit(3)
    )
    result_itens = await db.execute(stmt_itens)
    itens = result_itens.scalars().all()

    return entidade, itens
