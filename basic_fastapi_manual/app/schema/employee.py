from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class Employee(BaseModel):
    employee_id: int
    first_name: str = Field(max_length=40)
    last_name: str | None = Field(None, max_length=40)
    email: str | None = Field(default=None, max_length=40)
    phone_number: str | None = Field(default=None, max_length=20)
    hire_date: Optional[datetime] = None
    job_id: int = 0
    salary: float = Field(0.0)
    manager_id: int = 0
    department_id: int = 0
