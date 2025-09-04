#!/usr/bin/env python3
"""
Massive Stress Testing Suite for RobertAI
Simulates thousands of concurrent WhatsApp users for load validation
"""

import asyncio
import aiohttp
import time
import json
import random
import logging
import statistics
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import uuid
import hashlib
import hmac
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
import argparse
import csv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TestUser:
    """Usuario de prueba con estado"""
    user_id: str
    phone_number: str
    conversation_state: str = "initial"
    messages_sent: int = 0
    messages_received: int = 0
    last_message_time: float = 0
    response_times: List[float] = field(default_factory=list)
    errors: int = 0
    success_rate: float = 1.0

@dataclass
class TestScenario:
    """Escenario de prueba"""
    name: str
    message_types: List[str]
    message_frequency: float  # messages per second per user
    duration_seconds: int
    users_count: int
    ramp_up_time: int = 60  # seconds to reach full load
    
@dataclass
class TestResults:
    """Resultados de la prueba de carga"""
    scenario_name: str
    total_users: int
    total_messages_sent: int
    total_messages_received: int
    total_errors: int
    duration_seconds: float
    messages_per_second: float
    avg_response_time: float
    p50_response_time: float
    p90_response_time: float
    p95_response_time: float
    p99_response_time: float
    success_rate: float
    errors_by_type: Dict[str, int] = field(default_factory=dict)
    user_stats: List[Dict[str, Any]] = field(default_factory=list)

class MassiveStressTest:
    """Sistema de stress testing masivo"""
    
    def __init__(self,
                 base_url: str = "http://localhost:8000",
                 webhook_secret: str = "your-webhook-secret",
                 max_concurrent_sessions: int = 1000):
        
        self.base_url = base_url.rstrip('/')
        self.webhook_secret = webhook_secret
        self.max_concurrent_sessions = max_concurrent_sessions
        
        # Test users
        self.test_users: Dict[str, TestUser] = {}
        
        # Session management
        self.session: Optional[aiohttp.ClientSession] = None
        self.connector_limit = min(max_concurrent_sessions, 1000)
        
        # Statistics
        self.start_time: float = 0
        self.end_time: float = 0
        self.total_requests: int = 0
        self.total_errors: int = 0
        self.response_times: List[float] = []
        self.errors_by_type: Dict[str, int] = {}
        
        # Control flags
        self.running = False
        self.stop_requested = False
    
    async def initialize(self):
        """Inicializar cliente de pruebas"""
        
        # Create session with connection pooling
        connector = aiohttp.TCPConnector(
            limit=self.connector_limit,
            limit_per_host=self.connector_limit,
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )
        
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'User-Agent': 'RobertAI-StressTest/1.0'}
        )
        
        logger.info(f"Initialized stress test client (max concurrent: {self.connector_limit})")
    
    async def cleanup(self):
        """Limpiar recursos"""
        if self.session:
            await self.session.close()
        logger.info("Stress test client cleaned up")
    
    def generate_test_users(self, count: int) -> List[TestUser]:
        """Generar usuarios de prueba"""
        
        users = []
        
        for i in range(count):
            user_id = f"stress_user_{i:06d}"
            phone_number = f"521{random.randint(1000000000, 9999999999)}"  # Mexican numbers
            
            user = TestUser(
                user_id=user_id,
                phone_number=phone_number
            )
            
            users.append(user)
            self.test_users[user_id] = user
        
        logger.info(f"Generated {count} test users")
        return users
    
    def generate_webhook_payload(self, user: TestUser, message_type: str = "text") -> Dict[str, Any]:
        """Generar payload de webhook WhatsApp"""
        
        timestamp = str(int(time.time()))
        message_id = f"wamid.test_{uuid.uuid4().hex[:16]}"
        
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
        
        # Generate different message types
        if message_type == "text":
            message_content = {
                "from": user.phone_number,
                "id": message_id,
                "timestamp": timestamp,
                "text": {
                    "body": self._generate_random_text_message(user)
                },
                "type": "text"
            }
        
        elif message_type == "image":
            message_content = {
                "from": user.phone_number,
                "id": message_id,
                "timestamp": timestamp,
                "image": {
                    "id": "image_id_123",
                    "mime_type": "image/jpeg",
                    "sha256": "image_hash_456",
                    "caption": "Test image from stress test"
                },
                "type": "image"
            }
        
        elif message_type == "audio":
            message_content = {
                "from": user.phone_number,
                "id": message_id,
                "timestamp": timestamp,
                "audio": {
                    "id": "audio_id_123",
                    "mime_type": "audio/ogg",
                    "sha256": "audio_hash_456"
                },
                "type": "audio"
            }
        
        elif message_type == "interactive":
            message_content = {
                "from": user.phone_number,
                "id": message_id,
                "timestamp": timestamp,
                "interactive": {
                    "type": "button_reply",
                    "button_reply": {
                        "id": f"btn_{random.randint(1, 5)}",
                        "title": "Test Button"
                    }
                },
                "type": "interactive"
            }
        
        else:
            message_content = {
                "from": user.phone_number,
                "id": message_id,
                "timestamp": timestamp,
                "text": {
                    "body": f"Default message type: {message_type}"
                },
                "type": "text"
            }
        
        base_payload["entry"][0]["changes"][0]["value"]["messages"] = [message_content]
        
        return base_payload
    
    def _generate_random_text_message(self, user: TestUser) -> str:
        """Generar mensaje de texto aleatorio contextual"""
        
        messages_by_state = {
            "initial": [
                "Hola",
                "Buenos días",
                "Hola, necesito ayuda",
                "¿Cómo funciona esto?",
                "Quiero información",
            ],
            "conversation": [
                "Gracias por la información",
                "¿Puedes ayudarme con algo más?",
                "No entiendo bien",
                "¿Qué opciones tengo?",
                "Necesito más detalles",
                "¿Cuánto cuesta?",
                "¿Dónde puedo encontrar eso?",
                "¿Cuándo estará disponible?",
            ],
            "ending": [
                "Muchas gracias",
                "Perfecto, eso es todo",
                "Muy útil, gracias",
                "Hasta luego",
                "Adiós",
            ]
        }
        
        state = user.conversation_state
        if state not in messages_by_state:
            state = "conversation"
        
        return random.choice(messages_by_state[state])
    
    def generate_webhook_signature(self, payload: str) -> str:
        """Generar firma HMAC para webhook"""
        
        signature = hmac.new(
            self.webhook_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"sha256={signature}"
    
    async def send_webhook_message(self, user: TestUser, message_type: str = "text") -> Dict[str, Any]:
        """Enviar mensaje webhook simulado"""
        
        payload = self.generate_webhook_payload(user, message_type)
        payload_json = json.dumps(payload)
        signature = self.generate_webhook_signature(payload_json)
        
        headers = {
            'Content-Type': 'application/json',
            'X-Hub-Signature-256': signature,
            'X-Hub-Signature-Timestamp': str(int(time.time()))
        }
        
        start_time = time.time()
        
        try:
            async with self.session.post(
                f"{self.base_url}/webhooks/whatsapp",
                data=payload_json,
                headers=headers
            ) as response:
                
                response_time = time.time() - start_time
                user.response_times.append(response_time)
                self.response_times.append(response_time)
                
                response_text = await response.text()
                
                result = {
                    "user_id": user.user_id,
                    "message_type": message_type,
                    "status_code": response.status,
                    "response_time": response_time,
                    "response_text": response_text,
                    "success": 200 <= response.status < 300
                }
                
                if result["success"]:
                    user.messages_sent += 1
                else:
                    user.errors += 1
                    self.total_errors += 1
                    
                    error_key = f"http_{response.status}"
                    self.errors_by_type[error_key] = self.errors_by_type.get(error_key, 0) + 1
                
                self.total_requests += 1
                user.last_message_time = time.time()
                
                return result
        
        except asyncio.TimeoutError:
            response_time = time.time() - start_time
            user.errors += 1
            self.total_errors += 1
            self.errors_by_type["timeout"] = self.errors_by_type.get("timeout", 0) + 1
            
            return {
                "user_id": user.user_id,
                "message_type": message_type,
                "error": "timeout",
                "response_time": response_time,
                "success": False
            }
        
        except Exception as e:
            response_time = time.time() - start_time
            user.errors += 1
            self.total_errors += 1
            error_type = type(e).__name__
            self.errors_by_type[error_type] = self.errors_by_type.get(error_type, 0) + 1
            
            return {
                "user_id": user.user_id,
                "message_type": message_type,
                "error": str(e),
                "response_time": response_time,
                "success": False
            }
    
    async def simulate_user_behavior(self, user: TestUser, scenario: TestScenario):
        """Simular comportamiento de usuario durante la prueba"""
        
        messages_sent = 0
        target_messages = int(scenario.message_frequency * scenario.duration_seconds)
        
        # Calculate message interval
        interval = 1.0 / scenario.message_frequency if scenario.message_frequency > 0 else 1.0
        
        logger.debug(f"User {user.user_id} will send {target_messages} messages over {scenario.duration_seconds}s")
        
        while messages_sent < target_messages and self.running and not self.stop_requested:
            
            # Choose random message type from scenario
            message_type = random.choice(scenario.message_types)
            
            # Update conversation state
            if messages_sent == 0:
                user.conversation_state = "initial"
            elif messages_sent >= target_messages - 2:
                user.conversation_state = "ending"
            else:
                user.conversation_state = "conversation"
            
            # Send message
            result = await self.send_webhook_message(user, message_type)
            messages_sent += 1
            
            # Log significant events
            if messages_sent % 10 == 0 or not result["success"]:
                logger.debug(f"User {user.user_id}: {messages_sent}/{target_messages} messages, last: {result}")
            
            # Wait for next message (with some randomization)
            jitter = random.uniform(0.8, 1.2)  # ±20% jitter
            await asyncio.sleep(interval * jitter)
        
        # Update user stats
        if user.response_times:
            user.success_rate = (messages_sent - user.errors) / messages_sent if messages_sent > 0 else 0
        
        logger.debug(f"User {user.user_id} completed: {messages_sent} messages, {user.errors} errors")
    
    async def run_scenario(self, scenario: TestScenario) -> TestResults:
        """Ejecutar escenario de stress test"""
        
        logger.info(f"Starting stress test scenario: {scenario.name}")
        logger.info(f"Users: {scenario.users_count}, Duration: {scenario.duration_seconds}s, "
                   f"Message frequency: {scenario.message_frequency}/s per user")
        
        # Generate test users
        users = self.generate_test_users(scenario.users_count)
        
        # Reset statistics
        self.start_time = time.time()
        self.running = True
        self.stop_requested = False
        self.total_requests = 0
        self.total_errors = 0
        self.response_times.clear()
        self.errors_by_type.clear()
        
        # Create semaphore to limit concurrent users during ramp-up
        semaphore = asyncio.Semaphore(min(scenario.users_count, self.max_concurrent_sessions))
        
        async def limited_user_simulation(user):
            async with semaphore:
                await self.simulate_user_behavior(user, scenario)
        
        # Start user simulations with ramp-up
        tasks = []
        users_per_batch = max(1, scenario.users_count // (scenario.ramp_up_time or 1))
        
        logger.info(f"Ramping up {users_per_batch} users per second for {scenario.ramp_up_time} seconds")
        
        for i in range(0, len(users), users_per_batch):
            batch = users[i:i + users_per_batch]
            
            # Start batch of users
            batch_tasks = [
                asyncio.create_task(limited_user_simulation(user))
                for user in batch
            ]
            tasks.extend(batch_tasks)
            
            # Wait before next batch (unless it's the last batch)
            if i + users_per_batch < len(users):
                await asyncio.sleep(1)
        
        logger.info(f"All {len(users)} users started, running for {scenario.duration_seconds} seconds")
        
        # Wait for scenario duration or all tasks to complete
        try:
            await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=scenario.duration_seconds + scenario.ramp_up_time + 60  # Extra buffer
            )
        except asyncio.TimeoutError:
            logger.warning("Scenario timeout reached, stopping users...")
            self.stop_requested = True
            
            # Cancel remaining tasks
            for task in tasks:
                if not task.done():
                    task.cancel()
            
            await asyncio.gather(*tasks, return_exceptions=True)
        
        self.running = False
        self.end_time = time.time()
        
        # Calculate results
        results = self._calculate_results(scenario)
        
        logger.info(f"Scenario completed: {results.total_messages_sent} messages sent, "
                   f"{results.total_errors} errors, {results.success_rate:.2%} success rate")
        
        return results
    
    def _calculate_results(self, scenario: TestScenario) -> TestResults:
        """Calcular resultados del stress test"""
        
        duration = self.end_time - self.start_time
        total_messages_sent = sum(user.messages_sent for user in self.test_users.values())
        total_messages_received = total_messages_sent  # Assuming all sent messages are received
        total_errors = sum(user.errors for user in self.test_users.values())
        
        # Calculate response time statistics
        if self.response_times:
            avg_response_time = statistics.mean(self.response_times)
            sorted_times = sorted(self.response_times)
            p50 = statistics.quantiles(sorted_times, n=2)[0] if len(sorted_times) > 1 else sorted_times[0]
            p90 = statistics.quantiles(sorted_times, n=10)[8] if len(sorted_times) > 1 else sorted_times[0]
            p95 = statistics.quantiles(sorted_times, n=20)[18] if len(sorted_times) > 1 else sorted_times[0]
            p99 = statistics.quantiles(sorted_times, n=100)[98] if len(sorted_times) > 1 else sorted_times[0]
        else:
            avg_response_time = p50 = p90 = p95 = p99 = 0
        
        success_rate = (total_messages_sent - total_errors) / total_messages_sent if total_messages_sent > 0 else 0
        messages_per_second = total_messages_sent / duration if duration > 0 else 0
        
        # User statistics
        user_stats = []
        for user in self.test_users.values():
            user_stats.append({
                "user_id": user.user_id,
                "messages_sent": user.messages_sent,
                "errors": user.errors,
                "success_rate": user.success_rate,
                "avg_response_time": statistics.mean(user.response_times) if user.response_times else 0
            })
        
        return TestResults(
            scenario_name=scenario.name,
            total_users=len(self.test_users),
            total_messages_sent=total_messages_sent,
            total_messages_received=total_messages_received,
            total_errors=total_errors,
            duration_seconds=duration,
            messages_per_second=messages_per_second,
            avg_response_time=avg_response_time,
            p50_response_time=p50,
            p90_response_time=p90,
            p95_response_time=p95,
            p99_response_time=p99,
            success_rate=success_rate,
            errors_by_type=self.errors_by_type.copy(),
            user_stats=user_stats
        )
    
    def export_results_to_csv(self, results: TestResults, filename: str):
        """Exportar resultados a CSV"""
        
        # Summary results
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow(['Metric', 'Value'])
            
            # Summary metrics
            writer.writerow(['Scenario', results.scenario_name])
            writer.writerow(['Total Users', results.total_users])
            writer.writerow(['Total Messages Sent', results.total_messages_sent])
            writer.writerow(['Total Errors', results.total_errors])
            writer.writerow(['Duration (seconds)', f"{results.duration_seconds:.2f}"])
            writer.writerow(['Messages/Second', f"{results.messages_per_second:.2f}"])
            writer.writerow(['Success Rate', f"{results.success_rate:.2%}"])
            writer.writerow(['Avg Response Time (ms)', f"{results.avg_response_time * 1000:.2f}"])
            writer.writerow(['P50 Response Time (ms)', f"{results.p50_response_time * 1000:.2f}"])
            writer.writerow(['P90 Response Time (ms)', f"{results.p90_response_time * 1000:.2f}"])
            writer.writerow(['P95 Response Time (ms)', f"{results.p95_response_time * 1000:.2f}"])
            writer.writerow(['P99 Response Time (ms)', f"{results.p99_response_time * 1000:.2f}"])
            
            # Error breakdown
            writer.writerow([])
            writer.writerow(['Error Type', 'Count'])
            for error_type, count in results.errors_by_type.items():
                writer.writerow([error_type, count])
        
        # User details
        user_filename = filename.replace('.csv', '_users.csv')
        with open(user_filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow(['User ID', 'Messages Sent', 'Errors', 'Success Rate', 'Avg Response Time (ms)'])
            
            # User data
            for user_stat in results.user_stats:
                writer.writerow([
                    user_stat['user_id'],
                    user_stat['messages_sent'],
                    user_stat['errors'],
                    f"{user_stat['success_rate']:.2%}",
                    f"{user_stat['avg_response_time'] * 1000:.2f}"
                ])
        
        logger.info(f"Results exported to {filename} and {user_filename}")

# Predefined test scenarios
STRESS_TEST_SCENARIOS = {
    "warm_up": TestScenario(
        name="Warm Up Test",
        message_types=["text"],
        message_frequency=0.5,  # 1 message every 2 seconds
        duration_seconds=300,   # 5 minutes
        users_count=100,
        ramp_up_time=60
    ),
    
    "load_test": TestScenario(
        name="Load Test - Normal Usage",
        message_types=["text", "interactive"],
        message_frequency=1.0,   # 1 message per second
        duration_seconds=600,    # 10 minutes
        users_count=1000,
        ramp_up_time=120
    ),
    
    "stress_test": TestScenario(
        name="Stress Test - High Load",
        message_types=["text", "image", "interactive"],
        message_frequency=2.0,   # 2 messages per second
        duration_seconds=900,    # 15 minutes
        users_count=3000,
        ramp_up_time=180
    ),
    
    "spike_test": TestScenario(
        name="Spike Test - Sudden Load",
        message_types=["text"],
        message_frequency=5.0,   # 5 messages per second
        duration_seconds=300,    # 5 minutes
        users_count=5000,
        ramp_up_time=30  # Very fast ramp-up
    ),
    
    "endurance_test": TestScenario(
        name="Endurance Test - Long Duration",
        message_types=["text", "image", "audio", "interactive"],
        message_frequency=0.5,   # 1 message every 2 seconds
        duration_seconds=3600,   # 1 hour
        users_count=2000,
        ramp_up_time=300
    ),
    
    "multimodal_test": TestScenario(
        name="Multimodal Test - All Message Types",
        message_types=["text", "image", "audio", "interactive"],
        message_frequency=1.5,   # 1.5 messages per second
        duration_seconds=600,    # 10 minutes
        users_count=2000,
        ramp_up_time=120
    )
}

async def run_stress_test_suite():
    """Ejecutar suite completa de stress tests"""
    
    parser = argparse.ArgumentParser(description="RobertAI Massive Stress Test Suite")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL of the API")
    parser.add_argument("--webhook-secret", default="your-webhook-secret", help="Webhook secret")
    parser.add_argument("--scenario", choices=list(STRESS_TEST_SCENARIOS.keys()) + ["all"], 
                       default="load_test", help="Test scenario to run")
    parser.add_argument("--max-concurrent", type=int, default=1000, 
                       help="Maximum concurrent connections")
    parser.add_argument("--export-csv", action="store_true", 
                       help="Export results to CSV files")
    
    args = parser.parse_args()
    
    # Initialize stress tester
    stress_tester = MassiveStressTest(
        base_url=args.url,
        webhook_secret=args.webhook_secret,
        max_concurrent_sessions=args.max_concurrent
    )
    
    try:
        await stress_tester.initialize()
        
        # Determine scenarios to run
        if args.scenario == "all":
            scenarios_to_run = list(STRESS_TEST_SCENARIOS.keys())
        else:
            scenarios_to_run = [args.scenario]
        
        all_results = []
        
        for scenario_name in scenarios_to_run:
            scenario = STRESS_TEST_SCENARIOS[scenario_name]
            
            logger.info(f"\n{'='*60}")
            logger.info(f"RUNNING SCENARIO: {scenario.name}")
            logger.info(f"{'='*60}")
            
            # Run scenario
            results = await stress_tester.run_scenario(scenario)
            all_results.append(results)
            
            # Print results summary
            print(f"\n📊 RESULTS FOR {results.scenario_name}:")
            print(f"   Users: {results.total_users}")
            print(f"   Duration: {results.duration_seconds:.1f} seconds")
            print(f"   Messages Sent: {results.total_messages_sent:,}")
            print(f"   Messages/Second: {results.messages_per_second:.2f}")
            print(f"   Success Rate: {results.success_rate:.2%}")
            print(f"   Avg Response Time: {results.avg_response_time*1000:.2f} ms")
            print(f"   P90 Response Time: {results.p90_response_time*1000:.2f} ms")
            print(f"   P99 Response Time: {results.p99_response_time*1000:.2f} ms")
            print(f"   Total Errors: {results.total_errors:,}")
            
            if results.errors_by_type:
                print(f"   Error Breakdown:")
                for error_type, count in results.errors_by_type.items():
                    print(f"     {error_type}: {count:,}")
            
            # Export to CSV if requested
            if args.export_csv:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"stress_test_results_{scenario_name}_{timestamp}.csv"
                stress_tester.export_results_to_csv(results, filename)
            
            # Cool down between scenarios
            if scenario_name != scenarios_to_run[-1]:
                logger.info("Cooling down for 60 seconds before next scenario...")
                await asyncio.sleep(60)
        
        # Print overall summary
        if len(all_results) > 1:
            print(f"\n{'='*60}")
            print("OVERALL SUMMARY")
            print(f"{'='*60}")
            
            total_messages = sum(r.total_messages_sent for r in all_results)
            total_errors = sum(r.total_errors for r in all_results)
            avg_success_rate = statistics.mean([r.success_rate for r in all_results])
            
            print(f"   Scenarios Run: {len(all_results)}")
            print(f"   Total Messages: {total_messages:,}")
            print(f"   Total Errors: {total_errors:,}")
            print(f"   Average Success Rate: {avg_success_rate:.2%}")
            
        logger.info("Stress test suite completed successfully!")
        
    except Exception as e:
        logger.error(f"Stress test failed: {e}")
        raise
    
    finally:
        await stress_tester.cleanup()

if __name__ == "__main__":
    asyncio.run(run_stress_test_suite())