from pydantic import BaseModel
from typing import Optional, Any, List, Dict ,Required

class CategoriesSchema(BaseModel):
    _id: Optional[Any] = None
    name: Optional[str] = None
    id: Optional[str] = None
    isActive: Optional[bool] = None
    createdAt: Optional[Any] = None
    updatedAt: Optional[Any] = None

class ContactsSchema(BaseModel):
    _id: Optional[Any] = None
    email: Optional[str] = None
    user: Optional[Any] = None
    company: Optional[Any] = None
    name: Optional[str] = None
    mobile: Optional[str] = None
    message: Optional[str] = None
    file: Optional[Any] = None
    createdAt: Optional[Any] = None
    updatedAt: Optional[Any] = None

class SettingsSchema(BaseModel):
    _id: Optional[Any] = None
    type: Optional[str] = None
    isSiteInMaintenance: Optional[bool] = None
    createdAt: Optional[Any] = None
    updatedAt: Optional[Any] = None

class CompaniesSchema(BaseModel):
    _id: Optional[Any] = None
    email: Optional[str] = None
    user: Optional[Any] = None
    name: Optional[str] = None
    address: Optional[str] = None
    ACN: Optional[str] = None
    image: Optional[Any] = None
    category: Optional[Any] = None
    isActive: Optional[bool] = None
    isDeleted: Optional[bool] = None
    deletedAt: Optional[Any] = None
    deletedBy: Optional[Any] = None
    createdAt: Optional[Any] = None
    updatedAt: Optional[Any] = None
    ABN: Optional[str] = None

class TasksSchema(BaseModel):
    _id: Optional[Any] = None
    job: Optional[Any] = None
    company: Optional[Any] = None
    builder: Optional[Any] = None
    contractor: Optional[Any] = None
    disputant: Optional[Any] = None
    category: Optional[Any] = None
    status: Optional[str] = None
    requestedChange: Optional[bool] = None
    requestedRelease: Optional[bool] = None
    startDate: Optional[Any] = None
    pdf: Optional[str] = None
    po: Optional[str] = None
    milestone: Optional[list[Any]] = None
    timeline: Optional[list[Any]] = None
    createdAt: Optional[Any] = None
    updatedAt: Optional[Any] = None

class PermissionsSchema(BaseModel):
    _id: Optional[Any] = None
    name: Optional[str] = None
    method: Optional[str] = None
    displayName: Optional[str] = None
    module: Optional[str] = None
    type: Optional[int] = None
    createdAt: Optional[Any] = None
    updatedAt: Optional[Any] = None

class Chat_listsSchema(BaseModel):
    _id: Optional[Any] = None
    name: Optional[str] = None
    builderCompany: Optional[Any] = None
    contractorCompany: Optional[Any] = None
    task: Optional[Any] = None
    isActive: Optional[bool] = None
    createdAt: Optional[Any] = None
    updatedAt: Optional[Any] = None
    muteBuilder: Optional[bool] = None
    muteContractor: Optional[bool] = None

class LogsSchema(BaseModel):
    _id: Optional[Any] = None
    timestamp: Optional[Any] = None
    level: Optional[str] = None
    message: Optional[str] = None
    meta: Optional[dict[str, Any]] = None
    hostname: Optional[str] = None

class EmailLogsSchema(BaseModel):
    _id: Optional[Any] = None
    ref: Optional[Any] = None
    slug: Optional[str] = None
    status: Optional[str] = None
    token: Optional[Any] = None
    expiresIn: Optional[Any] = None
    fulfilledAt: Optional[Any] = None
    createdAt: Optional[Any] = None
    updatedAt: Optional[Any] = None

class HelpCenterSchema(BaseModel):
    _id: Optional[Any] = None
    title: Optional[str] = None
    question: Optional[str] = None
    answer: Optional[str] = None
    isActive: Optional[bool] = None
    createdAt: Optional[Any] = None
    updatedAt: Optional[Any] = None

class FriendsSchema(BaseModel):
    _id: Optional[Any] = None
    builder: Optional[Any] = None
    contractor: Optional[Any] = None
    company: Optional[Any] = None
    category: Optional[Any] = None
    sender: Optional[Any] = None
    status: Optional[str] = None
    createdAt: Optional[Any] = None
    updatedAt: Optional[Any] = None

class StaticPagesSchema(BaseModel):
    _id: Optional[Any] = None
    title: Optional[str] = None
    description: Optional[str] = None
    slug: Optional[str] = None
    createdAt: Optional[Any] = None
    updatedAt: Optional[Any] = None

class NotificationsSchema(BaseModel):
    _id: Optional[Any] = None
    user: Optional[Any] = None
    title: Optional[str] = None
    description: Optional[str] = None
    data: Optional[dict[str, Any]] = None
    type: Optional[str] = None
    isSent: Optional[bool] = None
    createdAt: Optional[Any] = None
    updatedAt: Optional[Any] = None
    isRead: Optional[bool] = None

class ManualLogsSchema(BaseModel):
    _id: Optional[Any] = None
    timestamp: Optional[Any] = None
    level: Optional[str] = None
    message: Optional[str] = None
    meta: Optional[dict[str, Any]] = None
    hostname: Optional[str] = None

class RolesSchema(BaseModel):
    _id: Optional[Any] = None
    name: Optional[str] = None
    permissions: Optional[list[Any]] = None
    type: Optional[int] = None
    isActive: Optional[bool] = None
    createdAt: Optional[Any] = None
    updatedAt: Optional[Any] = None

class UsersSchema(BaseModel):
    _id: Optional[Any] = None
    userId: Optional[str] = None
    password: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    role: Optional[Any] = None
    createdBy: Optional[Any] = None
    avatar: Optional[str] = None
    mobile: Optional[str] = None
    countryDialCode: Optional[str] = None
    countryIsoCode: Optional[str] = None
    fcm: Optional[Any] = None
    token: Optional[Any] = None
    creditLimit: Optional[Any] = None
    isSuspended: Optional[bool] = None
    isVerified: Optional[bool] = None
    isActive: Optional[bool] = None
    isDeleted: Optional[bool] = None
    deletedAt: Optional[Any] = None
    deletedBy: Optional[Any] = None
    createdAt: Optional[Any] = None
    updatedAt: Optional[Any] = None

class ChatsSchema(BaseModel):
    _id: Optional[Any] = None
    chatId: Optional[Any] = None
    sender: Optional[Any] = None
    receiver: Optional[Any] = None
    message: Optional[str] = None
    isRead: Optional[bool] = None
    file: Optional[Any] = None
    fileName: Optional[Any] = None
    fileType: Optional[Any] = None
    createdAt: Optional[Any] = None
    updatedAt: Optional[Any] = None

class JobsSchema(BaseModel):
    _id: Optional[Any] = None
    jobId: Optional[str] = None
    lotSearch: Optional[str] = None
    projectAddress: Optional[str] = None
    stampedPlan: Optional[str] = None
    buildingContract: Optional[str] = None
    buildingPermit: Optional[str] = None
    builder: Optional[Any] = None
    status: Optional[str] = None
    totalCost: Optional[int] = None
    commencementDate: Optional[Any] = None
    completionDate: Optional[Any] = None
    createdAt: Optional[Any] = None
    updatedAt: Optional[Any] = None
    longitude: Optional[Any] = None
    latitude: Optional[Any] = None
    geometry: Optional[dict[str, Any]] = None

class EmailTemplatesSchema(BaseModel):
    _id: Optional[Any] = None
    title: Optional[str] = None
    description: Optional[str] = None
    slug: Optional[str] = None
    values: Optional[list[Any]] = None
    isActive: Optional[bool] = None
    createdAt: Optional[Any] = None
    updatedAt: Optional[Any] = None

class AdminsSchema(BaseModel):
    _id: Optional[Any] = None
    email: Optional[str] = None
    password: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    role: Optional[Any] = None
    avatar: Optional[str] = None
    fcm: Optional[Any] = None
    isActive: Optional[bool] = None
    isDeleted: Optional[bool] = None
    deletedAt: Optional[Any] = None
    deletedBy: Optional[Any] = None
    createdAt: Optional[Any] = None
    updatedAt: Optional[Any] = None
    mobile: Optional[str] = None
    countryDialCode: Optional[str] = None
    countryIsoCode: Optional[str] = None
