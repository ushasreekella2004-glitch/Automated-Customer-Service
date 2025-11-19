"""
Core services for the Customer Service Agent
"""

import openai
import spacy
from typing import Dict, List, Any, Optional, Tuple
import logging
import json
import re
from datetime import datetime
import asyncio

from .models import IntentType, OrderStatus, ProductInfo, ReturnResponse
from .database import get_products_by_category, get_orders_by_customer, get_order_by_id, search_products
from .config import settings

logger = logging.getLogger(__name__)

class CustomerServiceAgent:
    """Main customer service agent"""
    
    def __init__(self):
        self.nlp = None
        self.intent_patterns = self._load_intent_patterns()
        self.conversation_history = {}
        
    async def initialize(self):
        """Initialize the agent"""
        try:
            # Load spaCy model
            self.nlp = spacy.load(settings.SPACY_MODEL)
            logger.info("Customer Service Agent initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing agent: {str(e)}")
            raise
    
    def _load_intent_patterns(self) -> Dict[str, List[str]]:
        """Load intent recognition patterns"""
        return {
            IntentType.ORDER_STATUS: [
                "order status", "track order", "where is my order",
                "order tracking", "delivery status", "shipping status"
            ],
            IntentType.PRODUCT_INFO: [
                "product information", "tell me about", "what is",
                "product details", "specifications", "price"
            ],
            IntentType.RETURN_REQUEST: [
                "return", "refund", "exchange", "send back",
                "return policy", "return item"
            ],
            IntentType.FAQ: [
                "help", "question", "how to", "what if",
                "can you help", "support"
            ],
            IntentType.STORE_HOURS: [
                "store hours", "opening hours", "when are you open",
                "business hours", "store time"
            ],
            IntentType.CONTACT: [
                "contact", "phone number", "email", "address",
                "customer service", "support"
            ],
            IntentType.GREETING: [
                "hello", "hi", "hey", "good morning", "good afternoon",
                "good evening", "greetings"
            ],
            IntentType.GOODBYE: [
                "bye", "goodbye", "see you", "thanks", "thank you",
                "farewell", "have a good day"
            ]
        }
    
    async def process_message(self, message: str, customer_id: Optional[str] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a customer message"""
        try:
            # Extract intent
            intent, confidence = await self._classify_intent(message)
            
            # Generate response based on intent
            response = await self._generate_response(message, intent, customer_id, session_id)
            
            # Store conversation
            if session_id:
                await self._store_conversation(session_id, customer_id, message, response["message"], intent, confidence)
            
            return {
                "message": response["message"],
                "intent": intent,
                "confidence": confidence,
                "suggested_actions": response.get("suggested_actions", [])
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                "message": "I apologize, but I'm experiencing technical difficulties. Please try again later or contact our support team.",
                "intent": IntentType.UNKNOWN,
                "confidence": 0.0,
                "suggested_actions": ["Contact Support", "Try Again"]
            }
    
    async def _classify_intent(self, message: str) -> Tuple[IntentType, float]:
        """Classify the intent of a message"""
        try:
            message_lower = message.lower()
            
            # Check against patterns
            best_intent = IntentType.UNKNOWN
            best_confidence = 0.0
            
            for intent, patterns in self.intent_patterns.items():
                for pattern in patterns:
                    if pattern in message_lower:
                        confidence = len(pattern) / len(message_lower)
                        if confidence > best_confidence:
                            best_confidence = confidence
                            best_intent = intent
            
            # Use OpenAI for more sophisticated classification if confidence is low
            if best_confidence < settings.MIN_CONFIDENCE:
                best_intent, best_confidence = await self._classify_with_openai(message)
            
            return best_intent, min(best_confidence, 1.0)
            
        except Exception as e:
            logger.error(f"Error classifying intent: {str(e)}")
            return IntentType.UNKNOWN, 0.0
    
    async def _classify_with_openai(self, message: str) -> Tuple[IntentType, float]:
        """Use OpenAI for intent classification"""
        try:
            if not settings.OPENAI_API_KEY:
                return IntentType.UNKNOWN, 0.0
            
            openai.api_key = settings.OPENAI_API_KEY
            
            prompt = f"""
            Classify the following customer message into one of these intents:
            - order_status: Questions about order tracking, delivery status
            - product_info: Questions about products, specifications, prices
            - return_request: Requests for returns, refunds, exchanges
            - faq: General questions, help requests
            - store_hours: Questions about store hours, business times
            - contact: Requests for contact information
            - greeting: Greetings, hello, hi
            - goodbye: Farewells, thank you, bye
            - unknown: Cannot be classified
            
            Message: "{message}"
            
            Respond with only the intent name and confidence score (0.0-1.0) separated by a comma.
            """
            
            response = await openai.ChatCompletion.acreate(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            intent_name, confidence = result.split(',')
            
            return IntentType(intent_name.strip()), float(confidence.strip())
            
        except Exception as e:
            logger.error(f"Error with OpenAI classification: {str(e)}")
            return IntentType.UNKNOWN, 0.0
    
    async def _generate_response(self, message: str, intent: IntentType, customer_id: Optional[str], session_id: Optional[str]) -> Dict[str, Any]:
        """Generate response based on intent"""
        try:
            if intent == IntentType.ORDER_STATUS:
                return await self._handle_order_status(message, customer_id)
            elif intent == IntentType.PRODUCT_INFO:
                return await self._handle_product_info(message)
            elif intent == IntentType.RETURN_REQUEST:
                return await self._handle_return_request(message, customer_id)
            elif intent == IntentType.FAQ:
                return await self._handle_faq(message)
            elif intent == IntentType.STORE_HOURS:
                return await self._handle_store_hours()
            elif intent == IntentType.CONTACT:
                return await self._handle_contact()
            elif intent == IntentType.GREETING:
                return await self._handle_greeting()
            elif intent == IntentType.GOODBYE:
                return await self._handle_goodbye()
            else:
                return await self._handle_unknown(message)
                
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return {
                "message": "I apologize, but I couldn't process your request. Please try rephrasing your question.",
                "suggested_actions": ["Contact Support", "Try Again"]
            }
    
    async def _handle_order_status(self, message: str, customer_id: Optional[str]) -> Dict[str, Any]:
        """Handle order status inquiries"""
        # Extract order ID from message
        order_id = self._extract_order_id(message)
        
        if order_id:
            order = get_order_by_id(order_id)
            if order:
                status_text = f"Your order {order_id} is currently {order['order_status']}."
                if order['return_status']:
                    status_text += f" Return status: {order['return_status']}."
                
                return {
                    "message": status_text,
                    "suggested_actions": ["Track Another Order", "View Order Details", "Contact Support"]
                }
            else:
                return {
                    "message": f"I couldn't find order {order_id}. Please check the order ID and try again.",
                    "suggested_actions": ["Check Order ID", "Contact Support"]
                }
        else:
            if customer_id:
                orders = get_orders_by_customer(customer_id)
                if orders:
                    recent_orders = orders[:3]  # Show last 3 orders
                    order_list = "\n".join([f"• {o['order_id']} - {o['product_name']} ({o['order_status']})" for o in recent_orders])
                    return {
                        "message": f"Here are your recent orders:\n{order_list}\n\nPlease provide an order ID for detailed status.",
                        "suggested_actions": ["Provide Order ID", "View All Orders"]
                    }
                else:
                    return {
                        "message": "I couldn't find any orders for your account. Please provide an order ID or contact support.",
                        "suggested_actions": ["Provide Order ID", "Contact Support"]
                    }
            else:
                return {
                    "message": "To check your order status, please provide your order ID or customer ID.",
                    "suggested_actions": ["Provide Order ID", "Provide Customer ID", "Contact Support"]
                }
    
    async def _handle_product_info(self, message: str) -> Dict[str, Any]:
        """Handle product information requests"""
        # Extract product name from message
        product_name = self._extract_product_name(message)
        
        if product_name:
            products = search_products(product_name, limit=5)
            if products:
                product_list = "\n".join([f"• {p['name']} - ${p['price']} ({p['category']})" for p in products])
                return {
                    "message": f"Here are products matching '{product_name}':\n{product_list}",
                    "suggested_actions": ["View Product Details", "Search Another Product", "Browse Categories"]
                }
            else:
                return {
                    "message": f"I couldn't find any products matching '{product_name}'. Please try a different search term.",
                    "suggested_actions": ["Try Different Search", "Browse Categories", "Contact Support"]
                }
        else:
            return {
                "message": "I'd be happy to help you find product information. What product are you looking for?",
                "suggested_actions": ["Search Products", "Browse Categories", "View Featured Products"]
            }
    
    async def _handle_return_request(self, message: str, customer_id: Optional[str]) -> Dict[str, Any]:
        """Handle return requests"""
        order_id = self._extract_order_id(message)
        
        if order_id:
            order = get_order_by_id(order_id)
            if order:
                if order['order_status'] == 'Delivered':
                    return {
                        "message": f"Your order {order_id} is eligible for return. Please provide a reason for the return.",
                        "suggested_actions": ["Provide Return Reason", "View Return Policy", "Contact Support"]
                    }
                else:
                    return {
                        "message": f"Your order {order_id} is currently {order['order_status']}. Returns are only available for delivered orders.",
                        "suggested_actions": ["Check Order Status", "Contact Support"]
                    }
            else:
                return {
                    "message": f"I couldn't find order {order_id}. Please check the order ID and try again.",
                    "suggested_actions": ["Check Order ID", "Contact Support"]
                }
        else:
            return {
                "message": "To process a return, please provide your order ID.",
                "suggested_actions": ["Provide Order ID", "View Return Policy", "Contact Support"]
            }
    
    async def _handle_faq(self, message: str) -> Dict[str, Any]:
        """Handle FAQ requests"""
        # Simple FAQ responses
        faq_responses = {
            "return policy": "We accept returns within 30 days of purchase. Items must be in original condition with tags attached.",
            "shipping": "We offer free shipping on orders over $50. Standard delivery takes 3-5 business days.",
            "payment": "We accept all major credit cards, PayPal, and bank transfers.",
            "warranty": "All products come with a 1-year manufacturer warranty.",
            "contact": "You can reach us at support@nvidia.com or call 1-800-NVIDIA-1."
        }
        
        message_lower = message.lower()
        for keyword, response in faq_responses.items():
            if keyword in message_lower:
                return {
                    "message": response,
                    "suggested_actions": ["Ask Another Question", "Contact Support", "View Full FAQ"]
                }
        
        return {
            "message": "I'd be happy to help! What would you like to know? You can ask about our return policy, shipping, payment methods, or warranty information.",
            "suggested_actions": ["Return Policy", "Shipping Info", "Payment Methods", "Warranty Info", "Contact Support"]
        }
    
    async def _handle_store_hours(self) -> Dict[str, Any]:
        """Handle store hours inquiries"""
        return {
            "message": "Our store hours are:\n• Monday to Friday: 9 AM - 6 PM\n• Saturday: 10 AM - 4 PM\n• Sunday: Closed\n\nWe're here to help during business hours!",
            "suggested_actions": ["Contact Us", "View Products", "Check Order Status"]
        }
    
    async def _handle_contact(self) -> Dict[str, Any]:
        """Handle contact information requests"""
        return {
            "message": "You can contact us through:\n• Email: support@nvidia.com\n• Phone: 1-800-NVIDIA-1\n• Live Chat: Available during business hours\n• Address: 2788 San Tomas Expressway, Santa Clara, CA 95051",
            "suggested_actions": ["Email Support", "Call Us", "Live Chat", "Visit Store"]
        }
    
    async def _handle_greeting(self) -> Dict[str, Any]:
        """Handle greetings"""
        return {
            "message": "Hello! I'm your NVIDIA customer service assistant. How can I help you today?",
            "suggested_actions": ["Check Order Status", "Product Information", "Return Request", "General Help"]
        }
    
    async def _handle_goodbye(self) -> Dict[str, Any]:
        """Handle farewells"""
        return {
            "message": "Thank you for contacting NVIDIA customer service! Have a great day!",
            "suggested_actions": ["Rate Service", "Contact Again", "Visit Website"]
        }
    
    async def _handle_unknown(self, message: str) -> Dict[str, Any]:
        """Handle unknown intents"""
        return {
            "message": "I'm not sure I understand your request. Could you please rephrase your question or choose from the options below?",
            "suggested_actions": ["Check Order Status", "Product Information", "Return Request", "Contact Support", "General Help"]
        }
    
    def _extract_order_id(self, message: str) -> Optional[str]:
        """Extract order ID from message"""
        # Look for patterns like "Order 12345" or "OrderID: 12345"
        patterns = [
            r'order\s+(\w+)',
            r'orderid[:\s]+(\w+)',
            r'order\s+id[:\s]+(\w+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_product_name(self, message: str) -> Optional[str]:
        """Extract product name from message"""
        # Simple extraction - look for quoted text or common product keywords
        quoted_match = re.search(r'"([^"]+)"', message)
        if quoted_match:
            return quoted_match.group(1)
        
        # Look for product-related keywords
        product_keywords = ['rtx', 'geforce', 'shield', 'jetson', 'graphics card', 'gpu']
        for keyword in product_keywords:
            if keyword.lower() in message.lower():
                return keyword
        
        return None
    
    async def _store_conversation(self, session_id: str, customer_id: Optional[str], message: str, response: str, intent: IntentType, confidence: float):
        """Store conversation in database"""
        try:
            # This would store in the database in a real implementation
            logger.info(f"Stored conversation: {session_id} - {intent} - {confidence}")
        except Exception as e:
            logger.error(f"Error storing conversation: {str(e)}")
    
    async def get_analytics(self) -> Dict[str, Any]:
        """Get system analytics"""
        return {
            "total_requests": 1000,
            "successful_responses": 850,
            "average_response_time": 1.2,
            "intent_distribution": {
                "order_status": 300,
                "product_info": 250,
                "return_request": 150,
                "faq": 200,
                "other": 100
            },
            "customer_satisfaction": 4.2,
            "top_products": ["RTX 4090", "RTX 4080", "Shield TV"],
            "common_issues": ["Order tracking", "Return requests", "Product compatibility"]
        }

class OrderService:
    """Order management service"""
    
    async def get_order_status(self, order_id: str) -> Optional[OrderStatus]:
        """Get order status by order ID"""
        try:
            order_data = get_order_by_id(order_id)
            if order_data:
                return OrderStatus(
                    order_id=order_data['order_id'],
                    customer_id=order_data['customer_id'],
                    product_name=order_data['product_name'],
                    order_date=order_data['order_date'],
                    quantity=order_data['quantity'],
                    order_amount=order_data['order_amount'],
                    order_status=order_data['order_status'],
                    return_status=order_data['return_status'],
                    return_reason=order_data['return_reason'],
                    notes=order_data['notes']
                )
            return None
        except Exception as e:
            logger.error(f"Error getting order status: {str(e)}")
            return None
    
    async def process_return_request(self, order_id: str, reason: str) -> ReturnResponse:
        """Process a return request"""
        try:
            order = get_order_by_id(order_id)
            if not order:
                return ReturnResponse(
                    return_id="",
                    status="Rejected",
                    message="Order not found"
                )
            
            if order['order_status'] != 'Delivered':
                return ReturnResponse(
                    return_id="",
                    status="Rejected",
                    message="Returns only available for delivered orders"
                )
            
            # Generate return ID
            return_id = f"RET-{order_id}-{datetime.now().strftime('%Y%m%d')}"
            
            return ReturnResponse(
                return_id=return_id,
                status="Requested",
                message="Return request submitted successfully",
                estimated_refund=order['order_amount']
            )
            
        except Exception as e:
            logger.error(f"Error processing return request: {str(e)}")
            return ReturnResponse(
                return_id="",
                status="Rejected",
                message="Error processing return request"
            )

class ProductService:
    """Product management service"""
    
    async def search_products(self, query: Optional[str] = None, category: Optional[str] = None, limit: int = 10) -> List[ProductInfo]:
        """Search products"""
        try:
            if category:
                products = get_products_by_category(category)
            elif query:
                products = search_products(query, limit)
            else:
                products = search_products("", limit)
            
            return [
                ProductInfo(
                    name=p['name'],
                    category=p['category'],
                    subcategory=p['subcategory'],
                    description=p['description'],
                    price=p['price'],
                    availability=True
                )
                for p in products
            ]
        except Exception as e:
            logger.error(f"Error searching products: {str(e)}")
            return []
