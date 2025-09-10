from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Any, Dict
from datetime import datetime
from bson import ObjectId


class PyObjectId(str):
    """Simple alias for ObjectId string in responses"""


# User
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: Optional[str]


class UserPublic(BaseModel):
    id: Optional[PyObjectId]
    email: EmailStr
    full_name: Optional[str]
    roles: List[str] = []
    projects: Dict[str, str] = {}  # project_id -> role
    is_active: bool = True
    created_at: Optional[datetime]


# Project
class ProjectCreate(BaseModel):
    title: str
    description: Optional[str]
    owner_id: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    tags: List[str] = []


class ProjectOut(BaseModel):
    id: Optional[PyObjectId]
    key: Optional[str]
    title: str
    description: Optional[str]
    owner_id: Optional[str]
    status: Optional[str]
    created_at: Optional[datetime]


# Task
class TaskCreate(BaseModel):
    project_id: str
    parent_id: Optional[str]
    title: str
    description: Optional[str]
    assignees: List[str] = []
    start_date: Optional[datetime]
    due_date: Optional[datetime]
    estimated_hours: Optional[float]


class TaskOut(BaseModel):
    id: Optional[PyObjectId]
    project_id: str
    title: str
    status: str
    assignees: List[str] = []


# Attachment metadata
class AttachmentCreate(BaseModel):
    filename: str
    mime_type: Optional[str]
    size: Optional[int]
    project_id: Optional[str]
    task_id: Optional[str]


class AttachmentOut(BaseModel):
    id: Optional[PyObjectId]
    filename: str
    mime_type: Optional[str]
    size: Optional[int]
    download_url: Optional[str]
    created_at: Optional[datetime]


# TimeEntry
class TimeEntryCreate(BaseModel):
    task_id: str
    project_id: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    notes: Optional[str]


class TimeEntryOut(BaseModel):
    id: Optional[PyObjectId]
    task_id: str
    project_id: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    duration_minutes: Optional[int]


# Comment
class CommentCreate(BaseModel):
    resource_type: str
    resource_id: str
    body: str


class CommentOut(BaseModel):
    id: Optional[PyObjectId]
    resource_type: str
    resource_id: str
    body: str
    author_id: Optional[str]
    created_at: Optional[datetime]


# Issue
class IssueCreate(BaseModel):
    project_id: str
    title: str
    description: Optional[str]
    severity: Optional[str]


class IssueOut(BaseModel):
    id: Optional[PyObjectId]
    project_id: str
    title: str
    description: Optional[str]
    status: str


# CustomFieldDefinition
class CustomFieldDefinitionCreate(BaseModel):
    resource_type: str
    name: str
    field_type: str
    options: List[str] = []
    required: bool = False
    visibility: str = "admins_only"


class CustomFieldDefinitionOut(BaseModel):
    id: Optional[PyObjectId]
    resource_type: str
    name: str
    field_type: str
    options: List[str] = []


# AuditLog
class AuditLogCreate(BaseModel):
    resource_type: str
    resource_id: str
    action: str
    user_id: Optional[str]
    details: Optional[Dict[str, Any]] = {}


class AuditLogOut(BaseModel):
    id: Optional[PyObjectId]
    resource_type: str
    resource_id: str
    action: str
    user_id: Optional[str]
    details: Optional[Dict[str, Any]]
    created_at: Optional[datetime]