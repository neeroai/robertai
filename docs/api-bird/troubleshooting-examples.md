# Troubleshooting & Interactive Examples

## 🔍 Common Issues & Solutions

### Authentication Issues

#### Issue: `401 Unauthorized - Invalid API Key`

**Problem**: Your API requests return `401 Unauthorized`

```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid API key",
    "request_id": "req_123"
  }
}
```

**Solutions**:
1. **Check API key format**:
   ```bash
   # ❌ Wrong - missing 'Bearer'
   curl -H "Authorization: bird_api_your_key"
   
   # ✅ Correct
   curl -H "Authorization: Bearer bird_api_your_key"
   ```

2. **Verify API key validity**:
   ```python
   # Test your API key
   import requests
   
   response = requests.get(
       'https://api.bird.com/v1/ai-employees',
       headers={'Authorization': f'Bearer {API_KEY}'}
   )
   
   if response.status_code == 401:
       print("❌ Invalid API key")
   else:
       print("✅ API key is valid")
   ```

3. **Check API key permissions**:
   - Ensure your API key has `AI Employees` permissions
   - Check if the key hasn't expired
   - Verify you're using the correct environment (prod vs sandbox)

#### Issue: `403 Forbidden - Insufficient Permissions`

**Solutions**:
```python
# Check which permissions your API key has
def check_permissions(api_key):
    endpoints_to_check = [
        '/v1/ai-employees',
        '/v1/knowledge-bases', 
        '/v1/conversations'
    ]
    
    for endpoint in endpoints_to_check:
        response = requests.get(
            f'https://api.bird.com{endpoint}',
            headers={'Authorization': f'Bearer {api_key}'}
        )
        
        if response.status_code == 403:
            print(f"❌ No permission for {endpoint}")
        else:
            print(f"✅ Has permission for {endpoint}")
```

### Performance Issues

#### Issue: High Response Times (>2 seconds)

**Problem**: AI responses are taking too long

**Diagnostic Script**:
```python
import time
import statistics

def measure_response_times(ai_employee_id, test_queries, iterations=5):
    response_times = []
    
    for query in test_queries:
        query_times = []
        
        for i in range(iterations):
            start_time = time.time()
            
            response = client.conversations.send_message(
                conversation_id=f"test_conv_{i}",
                content=query,
                ai_employee_id=ai_employee_id
            )
            
            end_time = time.time()
            query_times.append((end_time - start_time) * 1000)
        
        avg_time = statistics.mean(query_times)
        response_times.append({
            'query': query,
            'avg_time_ms': avg_time,
            'min_time_ms': min(query_times),
            'max_time_ms': max(query_times)
        })
    
    return response_times

# Test with sample queries
test_queries = [
    "¿Cuáles son sus horarios?",
    "¿Tienen descuentos disponibles?",
    "Necesito ayuda con mi pedido #12345"
]

results = measure_response_times("ai_employee_123", test_queries)
for result in results:
    print(f"Query: {result['query']}")
    print(f"  Average: {result['avg_time_ms']:.0f}ms")
    print(f"  Range: {result['min_time_ms']:.0f}ms - {result['max_time_ms']:.0f}ms")
```

**Solutions**:

1. **Optimize Knowledge Base**:
   ```python
   def optimize_knowledge_base(kb_id):
       # Get current documents
       docs = client.knowledge_bases.get_documents(kb_id)
       
       # Analyze document sizes
       large_docs = [doc for doc in docs if len(doc['content']) > 2000]
       
       print(f"Found {len(large_docs)} large documents to optimize")
       
       for doc in large_docs:
           # Split large documents into smaller chunks
           chunks = split_document_into_chunks(doc['content'], max_size=1500)
           
           # Delete original document
           client.knowledge_bases.delete_document(kb_id, doc['id'])
           
           # Create new smaller documents
           for i, chunk in enumerate(chunks):
               client.knowledge_bases.create_document(kb_id, {
                   'title': f"{doc['title']} - Parte {i+1}",
                   'content': chunk,
                   'metadata': {**doc['metadata'], 'chunk': i+1}
               })
   ```

2. **Use Appropriate Model**:
   ```python
   # For faster responses, use lighter models
   optimized_config = {
       "llm_config": {
           "provider": "openai",
           "model": "gpt-3.5-turbo",  # Faster than gpt-4
           "temperature": 0.7,
           "max_tokens": 300,  # Limit response length
           "top_p": 0.9
       }
   }
   
   client.ai_employees.update(ai_employee_id, optimized_config)
   ```

3. **Implement Response Caching**:
   ```python
   import hashlib
   import json
   from functools import lru_cache
   
   class ResponseCache:
       def __init__(self, max_size=1000):
           self.cache = {}
           self.max_size = max_size
       
       def get_cache_key(self, query, ai_employee_id):
           # Create hash of normalized query
           normalized = query.lower().strip()
           data = f"{ai_employee_id}:{normalized}"
           return hashlib.md5(data.encode()).hexdigest()
       
       def get_cached_response(self, query, ai_employee_id):
           key = self.get_cache_key(query, ai_employee_id)
           return self.cache.get(key)
       
       def cache_response(self, query, ai_employee_id, response):
           # Only cache high-confidence responses
           if response.confidence_score > 0.9:
               key = self.get_cache_key(query, ai_employee_id)
               
               if len(self.cache) >= self.max_size:
                   # Remove oldest entry
                   oldest_key = next(iter(self.cache))
                   del self.cache[oldest_key]
               
               self.cache[key] = response
   
   # Usage
   cache = ResponseCache()
   
   def send_message_with_cache(query, ai_employee_id):
       # Check cache first
       cached = cache.get_cached_response(query, ai_employee_id)
       if cached:
           return cached
       
       # Make API call
       response = client.conversations.send_message(
           conversation_id=f"conv_{int(time.time())}",
           content=query,
           ai_employee_id=ai_employee_id
       )
       
       # Cache the response
       cache.cache_response(query, ai_employee_id, response)
       
       return response
   ```

#### Issue: Low Confidence Scores (<0.7)

**Diagnostic Tool**:
```python
def analyze_low_confidence_responses(ai_employee_id, days=7):
    # Get recent conversations
    conversations = client.analytics.get_conversations(
        ai_employee_id=ai_employee_id,
        days_back=days,
        min_confidence=0.0,
        max_confidence=0.7
    )
    
    # Analyze patterns
    low_confidence_queries = []
    for conv in conversations:
        for message in conv['messages']:
            if message.get('confidence_score', 1.0) < 0.7:
                low_confidence_queries.append({
                    'query': message['content'],
                    'confidence': message['confidence_score'],
                    'response': message.get('ai_response', {}).get('content', ''),
                    'timestamp': message['timestamp']
                })
    
    # Find common patterns
    query_patterns = {}
    for item in low_confidence_queries:
        # Extract keywords
        keywords = extract_keywords(item['query'])
        for keyword in keywords:
            if keyword not in query_patterns:
                query_patterns[keyword] = []
            query_patterns[keyword].append(item)
    
    # Sort by frequency
    sorted_patterns = sorted(
        query_patterns.items(), 
        key=lambda x: len(x[1]), 
        reverse=True
    )
    
    print("🔍 Top topics with low confidence:")
    for keyword, items in sorted_patterns[:10]:
        print(f"  • {keyword}: {len(items)} occurrences")
        print(f"    Avg confidence: {sum(item['confidence'] for item in items) / len(items):.2f}")
    
    return sorted_patterns

# Run analysis
patterns = analyze_low_confidence_responses("ai_employee_123")
```

**Solutions**:
1. **Enhance Knowledge Base**:
   ```python
   def improve_knowledge_base_for_patterns(kb_id, low_confidence_patterns):
       for keyword, items in low_confidence_patterns[:5]:  # Top 5 patterns
           # Create targeted content
           content = generate_faq_content_for_keyword(keyword, items)
           
           # Add to knowledge base
           client.knowledge_bases.create_document(kb_id, {
               'title': f'FAQ: {keyword.title()}',
               'content': content,
               'type': 'faq',
               'metadata': {
                   'generated_from_analysis': True,
                   'keyword': keyword,
                   'improvement_date': '2024-01-25'
               }
           })
           
           print(f"✅ Added FAQ content for '{keyword}'")
   ```

### Rate Limiting Issues

#### Issue: `429 Too Many Requests`

**Problem**: You're hitting rate limits

```python
def handle_rate_limiting():
    import time
    from tenacity import retry, stop_after_attempt, wait_exponential
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60)
    )
    def api_call_with_retry(func, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if '429' in str(e):
                print("⚠️ Rate limited, waiting before retry...")
                time.sleep(60)  # Wait 1 minute
                raise
            else:
                raise
    
    # Usage
    def send_message_safe(conversation_id, content, ai_employee_id):
        return api_call_with_retry(
            client.conversations.send_message,
            conversation_id=conversation_id,
            content=content,
            ai_employee_id=ai_employee_id
        )
```

**Rate Limiting Best Practices**:
```python
import time
import threading

class RateLimitedClient:
    def __init__(self, requests_per_minute=60):
        self.requests_per_minute = requests_per_minute
        self.request_times = []
        self.lock = threading.Lock()
    
    def wait_if_needed(self):
        with self.lock:
            current_time = time.time()
            
            # Remove requests older than 1 minute
            self.request_times = [
                t for t in self.request_times 
                if current_time - t < 60
            ]
            
            # Check if we need to wait
            if len(self.request_times) >= self.requests_per_minute:
                sleep_time = 60 - (current_time - self.request_times[0])
                if sleep_time > 0:
                    print(f"⏳ Rate limit reached, waiting {sleep_time:.1f}s")
                    time.sleep(sleep_time)
                    # Remove the oldest request
                    self.request_times.pop(0)
            
            # Record this request
            self.request_times.append(current_time)
    
    def send_message(self, conversation_id, content, ai_employee_id):
        self.wait_if_needed()
        
        return client.conversations.send_message(
            conversation_id=conversation_id,
            content=content,
            ai_employee_id=ai_employee_id
        )

# Usage
rate_limited_client = RateLimitedClient(requests_per_minute=50)  # Stay under limit
```

## 🧪 Interactive Testing Tools

### API Health Checker

```python
def comprehensive_health_check(api_key):
    """Run comprehensive health check on your Bird.com setup"""
    
    print("🏥 Bird.com API Health Check")
    print("=" * 40)
    
    client = BirdClient(api_key=api_key)
    results = {}
    
    # 1. Test authentication
    print("\n1️⃣ Testing Authentication...")
    try:
        ai_employees = client.ai_employees.list()
        print("✅ Authentication successful")
        results['auth'] = True
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        results['auth'] = False
        return results
    
    # 2. Test AI Employees
    print("\n2️⃣ Testing AI Employees...")
    try:
        if ai_employees and len(ai_employees) > 0:
            print(f"✅ Found {len(ai_employees)} AI Employees")
            results['ai_employees'] = True
            test_employee = ai_employees[0]
        else:
            print("⚠️ No AI Employees found")
            results['ai_employees'] = False
    except Exception as e:
        print(f"❌ AI Employees check failed: {e}")
        results['ai_employees'] = False
    
    # 3. Test Knowledge Bases
    print("\n3️⃣ Testing Knowledge Bases...")
    try:
        knowledge_bases = client.knowledge_bases.list()
        if knowledge_bases and len(knowledge_bases) > 0:
            print(f"✅ Found {len(knowledge_bases)} Knowledge Bases")
            results['knowledge_bases'] = True
        else:
            print("⚠️ No Knowledge Bases found")
            results['knowledge_bases'] = False
    except Exception as e:
        print(f"❌ Knowledge Bases check failed: {e}")
        results['knowledge_bases'] = False
    
    # 4. Test Messaging (if we have an AI Employee)
    if results.get('ai_employees') and 'test_employee' in locals():
        print("\n4️⃣ Testing Messaging...")
        try:
            response = client.conversations.send_message(
                conversation_id="health_check_conv",
                content="Test message for health check",
                ai_employee_id=test_employee.id
            )
            
            if response and hasattr(response, 'ai_response'):
                print("✅ Messaging works")
                print(f"   Response time: {response.ai_response.get('response_time_ms', 'N/A')}ms")
                print(f"   Confidence: {response.ai_response.get('confidence_score', 'N/A')}")
                results['messaging'] = True
            else:
                print("⚠️ Messaging returned unexpected response")
                results['messaging'] = False
        except Exception as e:
            print(f"❌ Messaging test failed: {e}")
            results['messaging'] = False
    
    # 5. Summary
    print("\n📊 Health Check Summary")
    print("=" * 25)
    total_checks = len(results)
    passed_checks = sum(results.values())
    
    print(f"Passed: {passed_checks}/{total_checks} checks")
    
    if passed_checks == total_checks:
        print("🎉 All systems operational!")
    elif passed_checks > total_checks / 2:
        print("⚠️ Some issues found, but core functionality works")
    else:
        print("🚨 Multiple issues detected, please review configuration")
    
    return results

# Run health check
results = comprehensive_health_check("your_api_key_here")
```

### Conversation Simulator

```python
def simulate_conversation(ai_employee_id, conversation_script):
    """Simulate a multi-turn conversation"""
    
    print("🎭 Conversation Simulation")
    print("=" * 30)
    
    conversation_id = f"sim_conv_{int(time.time())}"
    
    for i, user_message in enumerate(conversation_script):
        print(f"\n👤 User: {user_message}")
        
        try:
            response = client.conversations.send_message(
                conversation_id=conversation_id,
                content=user_message,
                ai_employee_id=ai_employee_id
            )
            
            ai_response = response.ai_response.content
            confidence = response.ai_response.confidence_score
            response_time = response.ai_response.response_time_ms
            
            print(f"🤖 AI: {ai_response}")
            print(f"   📊 Confidence: {confidence:.2f} | Time: {response_time}ms")
            
            # Add delay to simulate realistic conversation
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Error in turn {i+1}: {e}")
            break
    
    print("\n✅ Conversation simulation complete")

# Example conversation script
customer_support_script = [
    "Hola, necesito ayuda",
    "¿Cuáles son sus horarios de atención?",
    "¿Tienen descuentos en productos de temporada?",
    "¿Cómo puedo hacer un pedido?",
    "¿Aceptan tarjetas de crédito?",
    "Gracias por la información"
]

simulate_conversation("ai_employee_123", customer_support_script)
```

### Performance Benchmark Tool

```python
def benchmark_ai_employee(ai_employee_id, test_queries, concurrent_users=5):
    """Benchmark AI Employee performance under load"""
    
    import concurrent.futures
    import statistics
    
    print(f"🏃‍♂️ Benchmarking AI Employee with {concurrent_users} concurrent users")
    print("=" * 60)
    
    def send_test_message(query, user_id):
        start_time = time.time()
        try:
            response = client.conversations.send_message(
                conversation_id=f"bench_conv_{user_id}_{int(time.time())}",
                content=query,
                ai_employee_id=ai_employee_id
            )
            
            end_time = time.time()
            
            return {
                'query': query,
                'user_id': user_id,
                'response_time_ms': (end_time - start_time) * 1000,
                'api_response_time_ms': response.ai_response.response_time_ms,
                'confidence_score': response.ai_response.confidence_score,
                'success': True
            }
        except Exception as e:
            end_time = time.time()
            return {
                'query': query,
                'user_id': user_id,
                'response_time_ms': (end_time - start_time) * 1000,
                'error': str(e),
                'success': False
            }
    
    # Run concurrent tests
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
        # Submit all test tasks
        futures = []
        for user_id in range(concurrent_users):
            for query in test_queries:
                future = executor.submit(send_test_message, query, user_id)
                futures.append(future)
        
        # Collect results
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            
            if result['success']:
                print(f"✅ User {result['user_id']}: {result['response_time_ms']:.0f}ms")
            else:
                print(f"❌ User {result['user_id']}: {result['error']}")
    
    # Analyze results
    successful_results = [r for r in results if r['success']]
    failed_results = [r for r in results if not r['success']]
    
    if successful_results:
        response_times = [r['response_time_ms'] for r in successful_results]
        confidence_scores = [r['confidence_score'] for r in successful_results]
        
        print(f"\n📊 Benchmark Results")
        print("=" * 20)
        print(f"Total requests: {len(results)}")
        print(f"Successful: {len(successful_results)} ({len(successful_results)/len(results)*100:.1f}%)")
        print(f"Failed: {len(failed_results)} ({len(failed_results)/len(results)*100:.1f}%)")
        print(f"\nResponse Time Statistics:")
        print(f"  Mean: {statistics.mean(response_times):.0f}ms")
        print(f"  Median: {statistics.median(response_times):.0f}ms")
        print(f"  Min: {min(response_times):.0f}ms")
        print(f"  Max: {max(response_times):.0f}ms")
        print(f"  95th percentile: {sorted(response_times)[int(len(response_times) * 0.95)]:.0f}ms")
        print(f"\nConfidence Score Statistics:")
        print(f"  Mean: {statistics.mean(confidence_scores):.2f}")
        print(f"  Min: {min(confidence_scores):.2f}")
        print(f"  Max: {max(confidence_scores):.2f}")
    
    return results

# Run benchmark
benchmark_queries = [
    "¿Cuáles son sus horarios?",
    "¿Tienen descuentos?",
    "¿Cómo puedo hacer un pedido?",
    "Necesito ayuda técnica",
    "¿Aceptan devoluciones?"
]

benchmark_results = benchmark_ai_employee("ai_employee_123", benchmark_queries)
```

## 🔗 Related Documentation

- [📚 API Reference](api-reference.md) - Complete technical documentation
- [⚡ Developer Quick Start](developer-quickstart.md) - 5-minute setup guide  
- [🔗 API Integrations](development/api-integrations.md) - Integration patterns
- [🔔 Webhooks](development/webhooks.md) - Event handling
- [📊 Monitoring](operations/monitoring.md) - Performance monitoring

---

*Need more help? Check our [Community Forum](https://community.bird.com) or contact [Developer Support](mailto:developers@bird.com)*