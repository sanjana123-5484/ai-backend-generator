
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def root():
    return {"message": "Generated FastAPI backend running"}


@router.get("/Books")
def get_Books():
    return {"message": "List all Books"}


@router.post("/Books")
def create_Books():
    return {"message": "Create Books"}


@router.put("/Books/{id}")
def update_Books(id: int):
    return {"message": "Update Books with id {id}"}


@router.delete("/Books/{id}")
def delete_Books(id: int):
    return {"message": "Delete Books with id {id}"}


@router.get("/Members")
def get_Members():
    return {"message": "List all Members"}


@router.post("/Members")
def create_Members():
    return {"message": "Create Members"}


@router.put("/Members/{id}")
def update_Members(id: int):
    return {"message": "Update Members with id {id}"}


@router.delete("/Members/{id}")
def delete_Members(id: int):
    return {"message": "Delete Members with id {id}"}


@router.get("/BorrowRecords")
def get_BorrowRecords():
    return {"message": "List all BorrowRecords"}


@router.post("/BorrowRecords")
def create_BorrowRecords():
    return {"message": "Create BorrowRecords"}


@router.put("/BorrowRecords/{id}")
def update_BorrowRecords(id: int):
    return {"message": "Update BorrowRecords with id {id}"}


@router.delete("/BorrowRecords/{id}")
def delete_BorrowRecords(id: int):
    return {"message": "Delete BorrowRecords with id {id}"}

