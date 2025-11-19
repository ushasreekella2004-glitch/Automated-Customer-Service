#!/usr/bin/env python3
"""
Test script for the Customer Service Agent API
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")

def test_chat_endpoint():
    """Test chat endpoint"""
    print("\nTesting chat endpoint...")
    
    # Test messages
    test_messages = [
        "Hello, I need help with my order",
        "What is the status of order 52768?",
        "Tell me about RTX 4090 graphics card",
        "I want to return my order",
        "What are your store hours?",
        "Thank you for your help"
    ]
    
    for message in test_messages:
        print(f"\nSending: '{message}'")
        try:
            response = requests.post(f"{BASE_URL}/api/chat", json={
                "message": message,
                "customer_id": "test_customer",
                "session_id": "test_session"
            })
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response: {data['response']}")
                print(f"   Intent: {data['intent']}")
                print(f"   Confidence: {data['confidence']:.2f}")
                if data.get('suggested_actions'):
                    print(f"   Suggested Actions: {data['suggested_actions']}")
            else:
                print(f"❌ Chat failed: {response.status_code}")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"❌ Chat error: {e}")
        
        time.sleep(1)  # Rate limiting

def test_order_status():
    """Test order status endpoint"""
    print("\nTesting order status endpoint...")
    
    test_order_ids = ["52768", "4065", "69268", "invalid_order"]
    
    for order_id in test_order_ids:
        print(f"\nTesting order ID: {order_id}")
        try:
            response = requests.get(f"{BASE_URL}/api/orders/{order_id}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Order found: {data['product_name']}")
                print(f"   Status: {data['order_status']}")
                print(f"   Amount: ${data['order_amount']}")
            elif response.status_code == 404:
                print(f"ℹ️  Order not found: {order_id}")
            else:
                print(f"❌ Order status failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Order status error: {e}")

def test_product_search():
    """Test product search endpoint"""
    print("\nTesting product search endpoint...")
    
    search_queries = [
        {"query": "RTX 4090"},
        {"query": "Shield"},
        {"category": "NVIDIA Electronics"},
        {"query": "graphics card", "limit": 5}
    ]
    
    for search in search_queries:
        print(f"\nSearching: {search}")
        try:
            response = requests.get(f"{BASE_URL}/api/products", params=search)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Found {len(data['products'])} products")
                for product in data['products'][:3]:  # Show first 3
                    print(f"   - {product['name']} (${product['price']})")
            else:
                print(f"❌ Product search failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Product search error: {e}")

def test_analytics():
    """Test analytics endpoint"""
    print("\nTesting analytics endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/analytics")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Analytics data retrieved")
            print(f"   Total requests: {data['total_requests']}")
            print(f"   Success rate: {data['successful_responses']}/{data['total_requests']}")
            print(f"   Avg response time: {data['average_response_time']}s")
        else:
            print(f"❌ Analytics failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Analytics error: {e}")

def main():
    """Run all tests"""
    print("🚀 Starting API tests...")
    print("=" * 50)
    
    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(2)
    
    # Run tests
    test_health_check()
    test_chat_endpoint()
    test_order_status()
    test_product_search()
    test_analytics()
    
    print("\n" + "=" * 50)
    print("🏁 Tests completed!")

if __name__ == "__main__":
    main()
