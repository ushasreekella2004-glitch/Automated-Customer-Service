"""
Pydantic models for the Customer Service Agent API
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class IntentType(str, Enum):
    """Intent classification types"""
    ORDER_STATUS = "order_status"
    PRODUCT_INFO = "product_info"
    RETURN_REQUEST = "return_request"
    FAQ = "faq"
    STORE_HOURS = "store_hours"
    CONTACT = "contact"
    GREETING = "greeting"
    GOODBYE = "goodbye"
    UNKNOWN = "unknown"

class OrderStatusType(str, Enum):
    """Order status types"""
    PENDING = "Pending"
    PROCESSING = "Processing"
    SHIPPED = "Shipped"
    IN_TRANSIT = "In Transit"
    DELIVERED = "Delivered"
    CANCELLED = "Cancelled"
    RETURNED = "Returned"
    RETURN_REQUESTED = "Return Requested"

class ReturnStatusType(str, Enum):
    """Return status types"""
    REQUESTED = "Requested"
    PENDING_APPROVAL = "Pending Approval"
    APPROVED = "Approved"
    REJECTED = "Rejected"

class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., description="User message")
    customer_id: Optional[str] = Field(None, description="Customer ID")
    session_id: Optional[str] = Field(None, description="Session ID")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")

class ChatResponse(BaseModel):
    """Chat response model"""
    response: str = Field(..., description="Agent response")
    intent: IntentType = Field(..., description="Detected intent")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    suggested_actions: Optional[List[str]] = Field(None, description="Suggested actions")
    session_id: Optional[str] = Field(None, description="Session ID")

class OrderStatus(BaseModel):
    """Order status model"""
    order_id: str = Field(..., description="Order ID")
    customer_id: str = Field(..., description="Customer ID")
    product_name: str = Field(..., description="Product name")
    order_date: datetime = Field(..., description="Order date")
    quantity: int = Field(..., description="Quantity")
    order_amount: float = Field(..., description="Order amount")
    status: OrderStatusType = Field(..., description="Order status")
    return_status: Optional[ReturnStatusType] = Field(None, description="Return status")
    return_reason: Optional[str] = Field(None, description="Return reason")
    notes: Optional[str] = Field(None, description="Additional notes")

class ProductInfo(BaseModel):
    """Product information model"""
    name: str = Field(..., description="Product name")
    category: str = Field(..., description="Product category")
    subcategory: str = Field(..., description="Product subcategory")
    description: str = Field(..., description="Product description")
    price: float = Field(..., description="Product price")
    availability: bool = Field(True, description="Product availability")

class ReturnRequest(BaseModel):
    """Return request model"""
    order_id: str = Field(..., description="Order ID")
    reason: str = Field(..., description="Return reason")
    customer_id: Optional[str] = Field(None, description="Customer ID")

class ReturnResponse(BaseModel):
    """Return response model"""
    return_id: str = Field(..., description="Return request ID")
    status: ReturnStatusType = Field(..., description="Return status")
    message: str = Field(..., description="Response message")
    estimated_refund: Optional[float] = Field(None, description="Estimated refund amount")

class FAQItem(BaseModel):
    """FAQ item model"""
    question: str = Field(..., description="FAQ question")
    answer: str = Field(..., description="FAQ answer")
    category: str = Field(..., description="FAQ category")
    tags: List[str] = Field(default_factory=list, description="FAQ tags")

class StoreInfo(BaseModel):
    """Store information model"""
    name: str = Field(..., description="Store name")
    hours: Dict[str, str] = Field(..., description="Store hours")
    address: str = Field(..., description="Store address")
    phone: str = Field(..., description="Store phone")
    email: str = Field(..., description="Store email")

class AnalyticsData(BaseModel):
    """Analytics data model"""
    total_requests: int = Field(..., description="Total requests")
    successful_responses: int = Field(..., description="Successful responses")
    average_response_time: float = Field(..., description="Average response time")
    intent_distribution: Dict[str, int] = Field(..., description="Intent distribution")
    customer_satisfaction: float = Field(..., description="Customer satisfaction score")
    top_products: List[Dict[str, Any]] = Field(..., description="Top products")
    common_issues: List[Dict[str, Any]] = Field(..., description="Common issues")

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
