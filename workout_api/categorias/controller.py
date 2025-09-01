from uuid import uuid4
from fastapi import APIRouter, Body, HTTPException, status, Query
from fastapi_pagination import Page, paginate
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from pydantic import UUID4

from workout_api.categorias.schemas import CategoriaIn, CategoriaOut
from workout_api.categorias.models import CategoriaModel
from workout_api.contrib.dependencies import DatabaseDependency

router = APIRouter()


# CREATE
@router.post('/', summary='Criar uma nova Categoria', status_code=status.HTTP_201_CREATED, response_model=CategoriaOut)
async def post(db_session: DatabaseDependency, categoria_in: CategoriaIn = Body(...)):
    try:
        categoria_out = CategoriaOut(id=uuid4(), **categoria_in.model_dump())
        categoria_model = CategoriaModel(**categoria_out.model_dump())

        db_session.add(categoria_model)
        await db_session.commit()
    except IntegrityError:
        await db_session.rollback()
        raise HTTPException(
            status_code=303,
            detail=f"Já existe uma categoria cadastrada com o nome: {categoria_in.nome}"
        )

    return categoria_out


# GET ALL COM PAGINAÇÃO E QUERY
@router.get('/', summary='Consultar todas as Categorias', response_model=Page[CategoriaOut])
async def query(db_session: DatabaseDependency, nome: str | None = Query(None, description="Filtrar por nome")):
    stmt = select(CategoriaModel)
    if nome:
        stmt = stmt.filter(CategoriaModel.nome.ilike(f"%{nome}%"))
    categorias = (await db_session.execute(stmt)).scalars().all()
    return paginate(categorias)


# GET BY ID
@router.get('/{id}', summary='Consultar uma Categoria pelo id', response_model=CategoriaOut)
async def get(id: UUID4, db_session: DatabaseDependency):
    categoria = (await db_session.execute(select(CategoriaModel).filter_by(id=id))).scalars().first()
    if not categoria:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Categoria não encontrada no id: {id}')
    return categoria
