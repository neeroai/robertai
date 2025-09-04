#!/usr/bin/env python3
"""
Locust Load Testing Configuration for RobertAI
Simple and scalable load testing using Locust framework
"""

import json
import random
import time
import hashlib
import hmac
import uuid
from locust import HttpUser, task, between, events
from locust.env import Environment
from locust.stats import stats_printer, stats_history
from locust import run_single_user
import logging

logger = logging.getLogger(__name__)

class RobertAIUser(HttpUser):
    """Simulated RobertAI user for load testing"""
    
    # Wait time between requests (in seconds)
    wait_time = between(1, 5)
    
    # Host will be set via command line or environment
    # host = "http://localhost:8000"
    
    def on_start(self):
        """Initialize user session"""
        # Generate unique user ID and phone number
        self.user_id = f"locust_user_{random.randint(100000, 999999)}"
        self.phone_number = f"521{random.randint(1000000000, 9999999999)}"
        self.message_count = 0
        self.conversation_state = "initial"
        
        # Webhook secret (should match server configuration)
        self.webhook_secret = "your-webhook-secret"
        
        logger.info(f"User {self.user_id} started with phone {self.phone_number}")
    
    def generate_webhook_signature(self, payload: str) -> str:
        """Generate HMAC signature for webhook payload"""
        signature = hmac.new(
            self.webhook_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"
    
    def create_whatsapp_webhook_payload(self, message_type: str = "text") -> dict:
        """Create WhatsApp webhook payload"""
        timestamp = str(int(time.time()))
        message_id = f"wamid.locust_{uuid.uuid4().hex[:16]}"
        
        base_payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
                    "changes": [
                        {
                            "value": {
                                "messaging_product": "whatsapp",
                                "metadata": {
                                    "display_phone_number": "15551234567",
                                    "phone_number_id": "PHONE_NUMBER_ID"
                                },
                                "messages": []
                            },
                            "field": "messages"
                        }
                    ]
                }
            ]
        }
        
        if message_type == "text":
            message_content = {
                "from": self.phone_number,
                "id": message_id,
                "timestamp": timestamp,
                "text": {
                    "body": self.get_contextual_message()
                },
                "type": "text"
            }
        elif message_type == "image":
            message_content = {
                "from": self.phone_number,
                "id": message_id,
                "timestamp": timestamp,
                "image": {
                    "id": "image_id_123",
                    "mime_type": "image/jpeg",
                    "sha256": "image_hash_456",
                    "caption": "Test image for load testing"
                },
                "type": "image"
            }
        elif message_type == "audio":
            message_content = {
                "from": self.phone_number,
                "id": message_id,
                "timestamp": timestamp,
                "audio": {
                    "id": "audio_id_789",
                    "mime_type": "audio/ogg",
                    "sha256": "audio_hash_123"
                },
                "type": "audio"
            }
        elif message_type == "interactive":
            message_content = {
                "from": self.phone_number,
                "id": message_id,
                "timestamp": timestamp,
                "interactive": {
                    "type": "button_reply",
                    "button_reply": {
                        "id": f"btn_{random.randint(1, 5)}",
                        "title": "Load Test Button"
                    }
                },
                "type": "interactive"
            }
        else:
            # Default to text
            message_content = {
                "from": self.phone_number,
                "id": message_id,
                "timestamp": timestamp,
                "text": {
                    "body": f"Load test message - {message_type}"
                },
                "type": "text"
            }
        
        base_payload["entry"][0]["changes"][0]["value"]["messages"] = [message_content]
        return base_payload
    
    def get_contextual_message(self) -> str:
        """Get contextual message based on conversation state"""
        messages_by_state = {
            "initial": [
                "Hola",
                "Buenos días",
                "Hola, necesito ayuda",
                "¿Qué tal?",
                "Saludos",
            ],
            "conversation": [
                "Gracias",
                "¿Puedes ayudarme?",
                "No entiendo",
                "¿Qué opciones hay?",
                "Más información por favor",
                "¿Cuánto cuesta?",
                "¿Dónde está eso?",
                "¿Cuándo?",
                "¿Cómo funciona?",
                "Necesito ayuda con esto",
            ],
            "ending": [
                "Perfecto, gracias",
                "Muy bien",
                "Hasta luego",
                "Adiós",
                "Muchas gracias",
            ]
        }
        
        return random.choice(messages_by_state.get(self.conversation_state, messages_by_state["conversation"]))
    
    def update_conversation_state(self):
        """Update conversation state based on message count"""
        if self.message_count == 0:
            self.conversation_state = "initial"
        elif self.message_count >= 8:
            self.conversation_state = "ending"
        else:
            self.conversation_state = "conversation"
    
    @task(50)  # 50% of requests will be text messages
    def send_text_message(self):
        """Send text message via webhook"""
        self.update_conversation_state()
        
        payload = self.create_whatsapp_webhook_payload("text")
        payload_json = json.dumps(payload)
        signature = self.generate_webhook_signature(payload_json)
        
        headers = {
            'Content-Type': 'application/json',
            'X-Hub-Signature-256': signature,
            'X-Hub-Signature-Timestamp': str(int(time.time()))
        }
        
        with self.client.post(
            "/webhooks/whatsapp",
            data=payload_json,
            headers=headers,
            name="webhook_text_message",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                self.message_count += 1
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(20)  # 20% of requests will be image messages
    def send_image_message(self):
        """Send image message via webhook"""
        payload = self.create_whatsapp_webhook_payload("image")
        payload_json = json.dumps(payload)
        signature = self.generate_webhook_signature(payload_json)
        
        headers = {
            'Content-Type': 'application/json',
            'X-Hub-Signature-256': signature,
            'X-Hub-Signature-Timestamp': str(int(time.time()))
        }
        
        with self.client.post(
            "/webhooks/whatsapp",
            data=payload_json,
            headers=headers,
            name="webhook_image_message",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                self.message_count += 1
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(15)  # 15% of requests will be interactive messages
    def send_interactive_message(self):
        """Send interactive message via webhook"""
        payload = self.create_whatsapp_webhook_payload("interactive")
        payload_json = json.dumps(payload)
        signature = self.generate_webhook_signature(payload_json)
        
        headers = {
            'Content-Type': 'application/json',
            'X-Hub-Signature-256': signature,
            'X-Hub-Signature-Timestamp': str(int(time.time()))
        }
        
        with self.client.post(
            "/webhooks/whatsapp",
            data=payload_json,
            headers=headers,
            name="webhook_interactive_message",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                self.message_count += 1
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(10)  # 10% of requests will be audio messages
    def send_audio_message(self):
        """Send audio message via webhook"""
        payload = self.create_whatsapp_webhook_payload("audio")
        payload_json = json.dumps(payload)
        signature = self.generate_webhook_signature(payload_json)
        
        headers = {
            'Content-Type': 'application/json',
            'X-Hub-Signature-256': signature,
            'X-Hub-Signature-Timestamp': str(int(time.time()))
        }
        
        with self.client.post(
            "/webhooks/whatsapp",
            data=payload_json,
            headers=headers,
            name="webhook_audio_message",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                self.message_count += 1
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(5)  # 5% of requests will be health checks
    def health_check(self):
        """Health check endpoint"""
        with self.client.get(
            "/health",
            name="health_check",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")
    
    def on_stop(self):
        """Cleanup when user stops"""
        logger.info(f"User {self.user_id} finished with {self.message_count} messages sent")

class RobertAIStressUser(HttpUser):
    """High-frequency stress testing user"""
    
    # Much faster requests for stress testing
    wait_time = between(0.1, 0.5)  # 0.1 to 0.5 seconds between requests
    
    def on_start(self):
        """Initialize stress user"""
        self.user_id = f"stress_user_{random.randint(100000, 999999)}"
        self.phone_number = f"521{random.randint(1000000000, 9999999999)}"
        self.webhook_secret = "your-webhook-secret"
        self.message_count = 0
    
    def generate_webhook_signature(self, payload: str) -> str:
        """Generate HMAC signature for webhook payload"""
        signature = hmac.new(
            self.webhook_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"
    
    @task
    def rapid_fire_messages(self):
        """Send rapid-fire text messages for stress testing"""
        timestamp = str(int(time.time()))
        message_id = f"wamid.stress_{uuid.uuid4().hex[:16]}"
        
        payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
                    "changes": [
                        {
                            "value": {
                                "messaging_product": "whatsapp",
                                "metadata": {
                                    "display_phone_number": "15551234567",
                                    "phone_number_id": "PHONE_NUMBER_ID"
                                },
                                "messages": [
                                    {
                                        "from": self.phone_number,
                                        "id": message_id,
                                        "timestamp": timestamp,
                                        "text": {
                                            "body": f"Stress test message {self.message_count}"
                                        },
                                        "type": "text"
                                    }
                                ]
                            },
                            "field": "messages"
                        }
                    ]
                }
            ]
        }
        
        payload_json = json.dumps(payload)
        signature = self.generate_webhook_signature(payload_json)
        
        headers = {
            'Content-Type': 'application/json',
            'X-Hub-Signature-256': signature,
            'X-Hub-Signature-Timestamp': str(int(time.time()))
        }
        
        with self.client.post(
            "/webhooks/whatsapp",
            data=payload_json,
            headers=headers,
            name="stress_message",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                self.message_count += 1
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")

# Custom event listeners for detailed logging
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when the test starts"""
    print("🚀 Starting RobertAI Load Test")
    print(f"Target host: {environment.host}")
    print(f"Expected users: {environment.parsed_options.num_users if environment.parsed_options else 'Unknown'}")
    print("-" * 50)

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when the test stops"""
    print("-" * 50)
    print("🏁 RobertAI Load Test Completed")
    
    stats = environment.stats.total
    
    print(f"📊 Test Results Summary:")
    print(f"   Total Requests: {stats.num_requests:,}")
    print(f"   Failed Requests: {stats.num_failures:,}")
    print(f"   Success Rate: {((stats.num_requests - stats.num_failures) / stats.num_requests * 100):.2f}%")
    print(f"   Average Response Time: {stats.avg_response_time:.2f} ms")
    print(f"   Max Response Time: {stats.max_response_time:.2f} ms")
    print(f"   Requests/Second: {stats.total_rps:.2f}")
    
    if stats.num_failures > 0:
        print(f"\n⚠️  Failed Requests by Type:")
        for method, endpoint in environment.stats.errors:
            error_stats = environment.stats.errors[method, endpoint]
            print(f"   {method} {endpoint}: {error_stats.occurrences} failures")

if __name__ == "__main__":
    # This allows running a single user for debugging
    # Usage: python locust_load_test.py
    run_single_user(RobertAIUser)