from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlmodel import SQLModel, Field, Session, create_engine, select
from contextlib import asynccontextmanager
from uuid import UUID, uuid4


class HeroBase(SQLModel):
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)


class Hero(HeroBase, table=True):
    id: UUID = Field(primary_key=True, default_factory=uuid4)
    secret_name: str


class HeroCreate(HeroBase):
    secret_name: str


class HeroUpdate(SQLModel):
    name: str | None = None
    age: int | None = None
    secret_name: str | None = None


class HeroPublic(HeroBase):
    id: UUID


engine = create_engine(
    "sqlite:///database.db", connect_args={"check_same_thread": False}
)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/heroes/", response_model=HeroPublic)
async def create_hero(session: SessionDep, hero: HeroCreate):
    new_hero = Hero.model_validate(hero)
    session.add(new_hero)
    session.commit()
    session.refresh(new_hero)
    return new_hero


@app.get("/heroes/", response_model=list[HeroPublic])
async def get_heroes(
    session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100
):
    heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
    return heroes


@app.get("/heroes/{hero_id}", response_model=HeroPublic)
async def get_hero(session: SessionDep, hero_id: UUID):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero


@app.patch("/heroes/{hero_id}", response_model=HeroPublic)
async def update_hero(session: SessionDep, hero_id: UUID, hero: HeroUpdate):
    old_hero = session.get(Hero, hero_id)
    if not old_hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    hero_data = hero.model_dump(exclude_unset=True)
    old_hero.sqlmodel_update(hero_data)
    session.add(old_hero)
    session.commit()
    session.refresh(old_hero)
    return old_hero


@app.delete("/heroes/{hero_id}")
async def delete_hero(session: SessionDep, hero_id: UUID):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    session.delete(hero)
    session.commit()
    return {"ok": True}
