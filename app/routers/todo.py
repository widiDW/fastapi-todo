from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from..database import get_db
from..models.course import Todo
from..models.user import User
from..schemas.todo import TodoCreate, TodoResponse, TodoUpdate
from..auth import get_current_user
from fastapi import Query
from math import ceil
from sqlalchemy import or_, desc, asc
from..schemas.pagination import PaginatedResponse


router = APIRouter(prefix="/todo", tags=["Todo"])

@router.post("/", response_model=TodoResponse, status_code=201)
def create_todo(
    todo: TodoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_todo = Todo(**todo.model_dump(), user_id=current_user.id)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@router.get("/", response_model=PaginatedResponse[TodoResponse])
def get_todos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Halaman ke berapa"),
    size: int = Query(10, ge=1, le=100, description="Jumlah data per halaman"),
    search: str | None = Query(None, description="Cari di title/description"),
    completed: bool | None = Query(None, description="Filter status"),
    sort: str = Query("newest", enum=["newest", "oldest"])
):
    
    # 1. Query dasar sesuai role admin
    query = db.query(Todo)
    if current_user.role!= "admin":
        query = query.filter(Todo.user_id == current_user.id)

    # 2. FILTER SEARCH
    if search:
        search_term = f"%{search}%"
        
        query = query.filter(
            or_(
                Todo.title.ilike(search_term), # ilike = case insensitive
                Todo.description.ilike(search_term)
            )
        )
        
    # 3. FILTER COMPLETED 
    if completed is not None: # pake 'is not None' karena False juga valid
        query = query.filter(Todo.completed == completed)
    
    # 4. SORTING COMPLETED
    if sort == "newest":
        query = query.order_by(desc(Todo.id)) # <-- ID gede = terbaru
    else: # oldest
        query = query.order_by(asc(Todo.id)) # <-- ID kecil = terlama

    # 5. Hitung total data buat pagination
    total = query.count()
    print("TOTAL DATA:", total)

    # 6. Hitung offset: skip data halaman sebelumnya
    offset = (page - 1) * size
    todos = query.offset(offset).limit(size).all()
    print("DATA DIKEMBALIIN:", len(todos))

    # 7. Hitung total halaman
    pages = ceil(total / size) if total > 0 else 1

    return {
        "total": total,
        "page": page,
        "size": size,
        "pages": pages,
        "data": todos
    }

@router.put("/{todo_id}", response_model=TodoResponse)
def update_todo(
    todo_id: int,
    todo_update: TodoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo nggak ketemu Jhon")

    if current_user.role != "admin" and todo.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Nggak bisa edit todo orang Jhon")

    update_data = todo_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(todo, key, value)

    db.commit()
    db.refresh(todo)
    return todo

@router.delete("/{todo_id}", status_code=204)
def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo nggak ketemu Jhon")

    if current_user.role != "admin" and todo.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Nggak bisa hapus todo orang Jhon")

    db.delete(todo)
    db.commit()
    return

@router.patch("/{todo_id}/toggle", response_model=TodoResponse)
def toggle_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Cari todo-nya dulu
    todo_query = db.query(Todo).filter(Todo.id == todo_id)
    todo = todo_query.first()

    if not todo:
        raise HTTPException(status_code=404, detail="Todo ga ketemu Jhon")

    # 2. Cek hak akses: bukan admin + bukan punya dia = tendang
    if current_user.role!= "admin" and todo.user_id!= current_user.id:
        raise HTTPException(status_code=403, detail="Bukan punya lu Jhon")

    # 3. TOGGLE MAGIC: False jadi True, True jadi False
    new_status = not todo.completed 
    todo_query.update({"completed": new_status}, synchronize_session=False)
    db.commit()

    # 4. Balikin data terbaru
    db.refresh(todo)
    return todo