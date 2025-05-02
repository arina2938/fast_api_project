from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_session
from app.models.models import User
from ..schemas import user as schema_user