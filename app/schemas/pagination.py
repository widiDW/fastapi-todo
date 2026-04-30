from pydantic import BaseModel
from typing import Generic, TypeVar, List

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    total: int # Total semua data di DB
    page: int # Halaman sekarang
    size: int # Jumlah data per halaman
    pages: int # Total halaman
    data: List[T] # Data aslinya

    class Config:
        from_attributes = True