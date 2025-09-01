from uuid import uuid4
from fastapi import APIRouter, Body, HTTPException, status, Query
from fastapi_pagination import Page, paginate
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from pydantic import UUID4

from workout_api.centro_treinamento.schemas import CentroTreinamentoIn, CentroTreinamentoOut
from workout_api.centro_treinamento.models import CentroTreinamentoModel
from workout_api.contrib.dependencies import DatabaseDependency

router = APIRouter()


# CREATE
@router.post('/', summary='Criar um novo Centro de treinamento', status_code=status.HTTP_201_CREATED, response_model=CentroTreinamentoOut)
async def post(db_session: DatabaseDependency, centro_in: CentroTreinamentoIn = Body(...)):
    try:
        centro_out = CentroTreinamentoOut(id=uuid4(), **centro_in.model_dump())
        centro_model = CentroTreinamentoModel(**centro_out.model_dump())

        db_session.add(centro_model)
        await db_session.commit()
    except IntegrityError:
        await db_session.rollback()
        raise HTTPException(
            status_code=303,
            detail=f"Já existe um centro de treinamento cadastrado com o nome: {centro_in.nome}"
        )

    return centro_out


# GET ALL COM PAGINAÇÃO E QUERY
@router.get('/', summary='Consultar todos os Centros de Treinamento', response_model=Page[CentroTreinamentoOut])
async def query(db_session: DatabaseDependency, nome: str | None = Query(None, description="Filtrar por nome")):
    stmt = select(CentroTreinamentoModel)
    if nome:
        stmt = stmt.filter(CentroTreinamentoModel.nome.ilike(f"%{nome}%"))
    centros = (await db_session.execute(stmt)).scalars().all()
    return paginate(centros)


# GET BY ID
@router.get('/{id}', summary='Consultar um Centro de Treinamento pelo id', response_model=CentroTreinamentoOut)
async def get(id: UUID4, db_session: DatabaseDependency):
    centro = (await db_session.execute(select(CentroTreinamentoModel).filter_by(id=id))).scalars().first()
    if not centro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Centro de treinamento não encontrado no id: {id}')
    return centro
