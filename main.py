"""
Limkokwing University Library Management API
PROG315 - Object-Oriented Programming 2
Author: [FRIEND'S FULL NAME]
Student ID: [FRIEND'S STUDENT ID]
"""

from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, Field
from typing import Optional
import asyncio
from datetime import date, timedelta

# ─────────────────────────────────────────────
# Application Setup
# ─────────────────────────────────────────────
app = FastAPI(
    title="LU Sierra Leone Library System",
    description=(
        "A FastAPI-powered library management system for Limkokwing University. "
        "Supports book registration, member management, loan tracking, and fine calculation."
    ),
    version="2.0.0",
)

# ─────────────────────────────────────────────
# Simulated Database (In-Memory)
# ─────────────────────────────────────────────
catalogue: dict[str, dict] = {
    "BK001": {"isbn": "BK001", "title": "Fluent Python", "author": "Luciano Ramalho",
               "genre": "Programming", "copies_total": 3, "copies_available": 2},
    "BK002": {"isbn": "BK002", "title": "Database System Concepts",
               "author": "Silberschatz", "genre": "Databases", "copies_total": 2,
               "copies_available": 2},
    "BK003": {"isbn": "BK003", "title": "Computer Networks",
               "author": "Andrew Tanenbaum", "genre": "Networking", "copies_total": 2,
               "copies_available": 1},
    "BK004": {"isbn": "BK004", "title": "Artificial Intelligence: A Modern Approach",
               "author": "Stuart Russell", "genre": "AI", "copies_total": 1,
               "copies_available": 0},
    "BK005": {"isbn": "BK005", "title": "Operating System Concepts",
               "author": "Abraham Silberschatz", "genre": "Systems", "copies_total": 2,
               "copies_available": 2},
}

members: dict[str, dict] = {
    "M001": {"member_id": "M001", "full_name": "Fatmata Bangura",
             "email": "fatmata@limkokwing.edu.sl", "active_loans": 0},
    "M002": {"member_id": "M002", "full_name": "Mohamed Conteh",
             "email": "mconteh@limkokwing.edu.sl", "active_loans": 1},
}

loans: dict[str, dict] = {
    "L001": {
        "loan_id": "L001", "member_id": "M002", "isbn": "BK003",
        "loan_date": str(date.today() - timedelta(days=18)),
        "due_date": str(date.today() - timedelta(days=4)),
        "status": "active",
    }
}

loan_counter: int = 2

# ─────────────────────────────────────────────
# Pydantic Schemas
# ─────────────────────────────────────────────
class BookSummary(BaseModel):
    isbn: str
    title: str
    author: str
    genre: str
    copies_available: int
    copies_total: int

class LoanRequest(BaseModel):
    member_id: str = Field(..., example="M001", description="Library member ID")
    isbn: str      = Field(..., example="BK001", description="Book ISBN code")

class LoanRecord(BaseModel):
    loan_id: str
    member_id: str
    isbn: str
    loan_date: str
    due_date: str
    status: str

class ReturnSummary(BaseModel):
    loan_id: str
    message: str
    days_overdue: int
    penalty_usd: float

class FineRecord(BaseModel):
    loan_id: str
    member_id: str
    member_name: str
    book_title: str
    due_date: str
    days_overdue: int
    penalty_usd: float

class NewBook(BaseModel):
    isbn: str        = Field(..., example="BK006")
    title: str       = Field(..., example="Web Development Essentials")
    author: str      = Field(..., example="Jon Duckett")
    genre: str       = Field(..., example="Web Development")
    copies_total: int = Field(..., example=2, ge=1)

# ─────────────────────────────────────────────
# ENDPOINT 1: GET /catalogue — Browse all books
# ─────────────────────────────────────────────
@app.get(
    "/catalogue",
    response_model=list[BookSummary],
    summary="Browse the full book catalogue",
    tags=["Books"],
)
async def browse_catalogue(
    genre: Optional[str] = Query(None, description="Filter by genre"),
    available_only: bool = Query(False, description="Show only books with available copies"),
) -> list[BookSummary]:
    """
    Returns the complete library catalogue.
    Optionally filter by genre or show only titles that have copies available.
    """
    results: list[dict] = list(catalogue.values())

    if genre:
        results = [b for b in results if genre.lower() in b["genre"].lower()]
    if available_only:
        results = [b for b in results if b["copies_available"] > 0]

    return results


# ─────────────────────────────────────────────
# ENDPOINT 2: POST /catalogue — Add a new book
# ─────────────────────────────────────────────
@app.post(
    "/catalogue",
    response_model=BookSummary,
    status_code=201,
    summary="Add a new book to the catalogue",
    tags=["Books"],
)
async def add_book(book: NewBook) -> BookSummary:
    """
    Registers a new book title in the library catalogue.
    Used by library staff when new stock arrives.
    """
    if book.isbn in catalogue:
        raise HTTPException(
            status_code=409,
            detail=f"A book with ISBN '{book.isbn}' already exists in the catalogue.",
        )

    await asyncio.sleep(0.05)  # Simulate async DB write

    new_entry: dict = {
        "isbn": book.isbn,
        "title": book.title,
        "author": book.author,
        "genre": book.genre,
        "copies_total": book.copies_total,
        "copies_available": book.copies_total,
    }
    catalogue[book.isbn] = new_entry
    return new_entry


# ─────────────────────────────────────────────
# ENDPOINT 3: POST /loans — Issue a loan
# ─────────────────────────────────────────────
@app.post(
    "/loans",
    response_model=LoanRecord,
    summary="Issue a book loan to a member",
    tags=["Loans"],
)
async def issue_loan(request: LoanRequest) -> LoanRecord:
    """
    Issues a book loan to a library member.
    Validates the member and book, checks copy availability,
    and creates a loan record with a 14-day return window.
    Decrements the available copy count for that title.
    """
    global loan_counter

    if request.member_id not in members:
        raise HTTPException(404, f"Member '{request.member_id}' does not exist.")

    if request.isbn not in catalogue:
        raise HTTPException(404, f"Book ISBN '{request.isbn}' not found in catalogue.")

    book = catalogue[request.isbn]
    if book["copies_available"] < 1:
        raise HTTPException(
            400,
            f"No available copies of '{book['title']}'. "
            f"All {book['copies_total']} copies are currently on loan.",
        )

    await asyncio.sleep(0.05)  # Simulate async DB write

    loan_date: date = date.today()
    due_date: date  = loan_date + timedelta(days=14)
    loan_id: str    = f"L{loan_counter:03d}"

    record: dict = {
        "loan_id":   loan_id,
        "member_id": request.member_id,
        "isbn":      request.isbn,
        "loan_date": str(loan_date),
        "due_date":  str(due_date),
        "status":    "active",
    }

    loans[loan_id] = record
    catalogue[request.isbn]["copies_available"] -= 1
    members[request.member_id]["active_loans"]  += 1
    loan_counter += 1

    return record


# ─────────────────────────────────────────────
# ENDPOINT 4: PATCH /loans/{loan_id}/return — Return a book
# ─────────────────────────────────────────────
@app.patch(
    "/loans/{loan_id}/return",
    response_model=ReturnSummary,
    summary="Process a book return",
    tags=["Loans"],
)
async def return_book(
    loan_id: str = Path(..., example="L001", description="The loan ID to close"),
) -> ReturnSummary:
    """
    Processes a book return. Marks the loan as returned, restores the
    available copy count, and calculates any penalty fees for late returns
    at a rate of $0.75 per overdue day.
    """
    if loan_id not in loans:
        raise HTTPException(404, f"Loan record '{loan_id}' not found.")

    record = loans[loan_id]
    if record["status"] == "returned":
        raise HTTPException(400, f"Loan '{loan_id}' has already been closed.")

    await asyncio.sleep(0.05)  # Simulate async DB write

    today: date    = date.today()
    due: date      = date.fromisoformat(record["due_date"])
    days_overdue   = max(0, (today - due).days)
    penalty: float = round(days_overdue * 0.75, 2)

    record["status"] = "returned"
    catalogue[record["isbn"]]["copies_available"] += 1
    members[record["member_id"]]["active_loans"]  -= 1

    return ReturnSummary(
        loan_id=loan_id,
        message="Return processed successfully.",
        days_overdue=days_overdue,
        penalty_usd=penalty,
    )


# ─────────────────────────────────────────────
# ENDPOINT 5: GET /fines — View outstanding fines
# ─────────────────────────────────────────────
@app.get(
    "/fines",
    response_model=list[FineRecord],
    summary="View all outstanding overdue fines",
    tags=["Fines"],
)
async def get_outstanding_fines() -> list[FineRecord]:
    """
    Returns a report of all active loans that have passed their due date.
    Calculates each member's accumulated penalty at $0.75 per overdue day.
    Intended for use by library administrators.
    """
    today: date           = date.today()
    report: list[FineRecord] = []

    for loan in loans.values():
        if loan["status"] != "active":
            continue
        due: date = date.fromisoformat(loan["due_date"])
        if today <= due:
            continue
        days_overdue: int  = (today - due).days
        member             = members.get(loan["member_id"], {})
        book               = catalogue.get(loan["isbn"], {})

        report.append(FineRecord(
            loan_id      = loan["loan_id"],
            member_id    = loan["member_id"],
            member_name  = member.get("full_name", "Unknown"),
            book_title   = book.get("title", "Unknown"),
            due_date     = loan["due_date"],
            days_overdue = days_overdue,
            penalty_usd  = round(days_overdue * 0.75, 2),
        ))

    return report


# ─────────────────────────────────────────────
# Async Simulation: Concurrent Member Activity
# ─────────────────────────────────────────────
async def member_borrow(member_id: str, isbn: str) -> str:
    """Simulates a member borrowing a book asynchronously."""
    await asyncio.sleep(0.08)
    if isbn not in catalogue:
        return f"[{member_id}] ERROR — Book {isbn} not found."
    if catalogue[isbn]["copies_available"] < 1:
        return f"[{member_id}] FAILED — No copies of {isbn} available."
    catalogue[isbn]["copies_available"] -= 1
    return f"[{member_id}] SUCCESS — Borrowed '{catalogue[isbn]['title']}'."


async def member_return(member_id: str, isbn: str) -> str:
    """Simulates a member returning a book asynchronously."""
    await asyncio.sleep(0.06)
    for loan in loans.values():
        if (loan["member_id"] == member_id
                and loan["isbn"] == isbn
                and loan["status"] == "active"):
            loan["status"] = "returned"
            catalogue[isbn]["copies_available"] += 1
            return f"[{member_id}] SUCCESS — Returned '{catalogue[isbn]['title']}'."
    return f"[{member_id}] FAILED — No active loan found for Book {isbn}."


async def simulate_concurrent_activity() -> None:
    """
    Simulates multiple library members performing actions simultaneously
    using asyncio.gather(). This demonstrates how the API handles concurrent
    requests without blocking — each coroutine yields control at await points,
    allowing others to progress at the same time.
    """
    print("\n======= Concurrent Member Activity Simulation =======")
    tasks = [
        member_borrow("M001", "BK001"),
        member_borrow("M001", "BK002"),
        member_return("M002", "BK003"),
        member_borrow("M002", "BK005"),
    ]
    outcomes = await asyncio.gather(*tasks)
    for outcome in outcomes:
        print(outcome)
    print("=====================================================\n")


@app.on_event("startup")
async def on_startup() -> None:
    """Run concurrent simulation when server starts (for demo purposes)."""
    await simulate_concurrent_activity()


# ─────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
