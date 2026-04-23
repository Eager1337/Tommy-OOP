
## 📌 Project Description

A RESTful Library Management API built with **Python FastAPI** for Limkokwing University Sierra Leone. The system manages the full book lifecycle — from cataloguing new arrivals to tracking loans, returns, and overdue penalties — while supporting multiple concurrent users through asynchronous request handling.

---

## ✨ Features

- 📚 Browse the full book catalogue with genre and availability filters
- ➕ Add new books to the catalogue (staff use)
- 🔖 Issue book loans with automatic 14-day due dates
- 🔄 Process returns with automatic penalty calculation ($0.75/day)
- 💰 Generate outstanding fines report for administrators
- ⚡ Asynchronous request handling for concurrent user support
- ✅ Strict type validation using Pydantic models

---

## 🛠️ Technologies Used

| Technology | Role |
|------------|------|
| Python 3.11+ | Core programming language |
| FastAPI | Web API framework |
| Uvicorn | ASGI server |
| Pydantic v2 | Data validation & type enforcement |
| Asyncio | Concurrency model |

---

## ⚙️ Installation

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/lu-library-system-api.git
cd lu-library-system-api

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/catalogue` | Browse all books (filter by genre / availability) |
| POST | `/catalogue` | Add a new book to the catalogue |
| POST | `/loans` | Issue a book loan to a member |
| PATCH | `/loans/{loan_id}/return` | Process a book return |
| GET | `/fines` | View all outstanding overdue fines |

---

## 📖 Interactive Docs

After starting the server, visit:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 📁 Project Structure

```
lu-library-system-api/
│
├── main.py              # FastAPI app — all endpoints + async simulation
├── requirements.txt     # Dependencies
├── README.md            # Project documentation
└── .gitignore           # Excludes venv, cache, secrets
```

---

## 🌍 SDG Alignment

Aligned with **SDG 4 – Quality Education**: the system removes barriers to library access by enabling students and staff to manage resources digitally, reducing wasted time and improving access to educational materials for all.

---



