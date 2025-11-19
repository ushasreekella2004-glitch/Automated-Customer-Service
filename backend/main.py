"""
Automated Customer Service Agent - Main FastAPI Application
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn
import logging
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

from .database import init_db
from .models import ChatRequest, ChatResponse, OrderStatus, ProductInfo
from .services import CustomerServiceAgent, OrderService, ProductService
from .auth import verify_token
from .config import settings

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Automated Customer Service Agent...")
    await init_db()
    logger.info("Database initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Automated Customer Service Agent...")

# Initialize FastAPI app
app = FastAPI(
    title="Automated Customer Service Agent",
    description="AI-powered virtual assistant for customer service",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
customer_agent = CustomerServiceAgent()
order_service = OrderService()
product_service = ProductService()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Automated Customer Service Agent API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "services": {
            "database": "connected",
            "ai_model": "loaded",
            "cache": "active"
        }
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Main chat endpoint for customer interactions
    """
    try:
        # Verify authentication
        await verify_token(credentials.credentials)
        
        # Process the chat request
        response = await customer_agent.process_message(
            message=request.message,
            customer_id=request.customer_id,
            session_id=request.session_id
        )
        
        return ChatResponse(
            response=response["message"],
            intent=response["intent"],
            confidence=response["confidence"],
            suggested_actions=response.get("suggested_actions", []),
            session_id=request.session_id
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.get("/api/orders/{order_id}", response_model=OrderStatus)
async def get_order_status(
    order_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get order status by order ID
    """
    try:
        await verify_token(credentials.credentials)
        
        order = await order_service.get_order_status(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        return order
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching order status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.get("/api/products")
async def search_products(
    query: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 10,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Search products by query or category
    """
    try:
        await verify_token(credentials.credentials)
        
        products = await product_service.search_products(
            query=query,
            category=category,
            limit=limit
        )
        
        return {
            "products": products,
            "total": len(products),
            "query": query,
            "category": category
        }
        
    except Exception as e:
        logger.error(f"Error searching products: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.post("/api/returns")
async def process_return_request(
    order_id: str,
    reason: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Process a return request
    """
    try:
        await verify_token(credentials.credentials)
        
        result = await order_service.process_return_request(
            order_id=order_id,
            reason=reason
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing return request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.get("/api/analytics")
async def get_analytics(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get system analytics (admin only)
    """
    try:
        await verify_token(credentials.credentials)
        
        analytics = await customer_agent.get_analytics()
        return analytics
        
    except Exception as e:
        logger.error(f"Error fetching analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
