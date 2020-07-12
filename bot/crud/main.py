from typing import Optional

from sqlalchemy.orm import Session, Query

from ..database import Base, session


def get_query(model: Base, db: Optional[Session] = None):
    return db.query(model) if db else model.query


def find(model: Base, db: Optional[Session] = None, **kwargs):
    if not kwargs:
        raise TypeError('You must provide at least one keyword argument')
    query = get_query(model, db)
    return query.filter_by(**kwargs).first()


def get(model: Base, obj_id: int):
    return model.query.get(obj_id)


def create_one(model: Base, db: Optional[Session] = None, **kwargs):
    obj = model(**kwargs)
    if db is None:
        db = session
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_or_create(model: Base, db: Optional[Session] = None, **kwargs):
    obj = find(model, db, **kwargs)
    if obj is None:
        obj = create_one(model, db, **kwargs)
    return obj


def paginate(query: Query, page: int, per_page: int):
    start = (page - 1) * per_page

    return (
        query
        .slice(start, start + per_page)
    )
