# 13 - Seguridad y Compliance

## 🔐 Framework de Seguridad Integral

### Arquitectura de Seguridad en Capas

```
┌─────────────────────────────────────────────────────────────┐
│                    Capa 1: Perímetro                         │
│  • WAF (Web Application Firewall)                           │
│  • DDoS Protection                                          │
│  • Rate Limiting                                            │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                 Capa 2: Autenticación                        │
│  • Multi-factor Authentication                              │
│  • OAuth 2.0 / JWT                                         │
│  • API Key Management                                       │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                  Capa 3: Autorización                        │
│  • RBAC (Role-Based Access Control)                        │
│  • Attribute-Based Access Control                          │
│  • Policy Engine                                            │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│               Capa 4: Protección de Datos                    │
│  • Encryption at Rest (AES-256)                            │
│  • Encryption in Transit (TLS 1.3)                         │
│  • Data Masking & Tokenization                             │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                  Capa 5: Auditoría                          │
│  • Comprehensive Logging                                     │
│  • Immutable Audit Trail                                    │
│  • Real-time Monitoring                                     │
└─────────────────────────────────────────────────────────────┘
```

## 🛡️ Protección de Datos

### Clasificación de Datos

```python
class DataClassification:
    """Sistema de clasificación de datos"""
    
    CLASSIFICATIONS = {
        'public': {
            'description': 'Información pública',
            'examples': ['Catálogo de productos', 'Políticas generales'],
            'encryption': 'optional',
            'access': 'unrestricted'
        },
        'internal': {
            'description': 'Uso interno',
            'examples': ['Métricas agregadas', 'Reportes'],
            'encryption': 'required',
            'access': 'employees_only'
        },
        'confidential': {
            'description': 'Información confidencial',
            'examples': ['Datos de clientes', 'Estrategias'],
            'encryption': 'required',
            'access': 'need_to_know'
        },
        'restricted': {
            'description': 'Altamente sensible',
            'examples': ['PII', 'Datos financieros', 'Credenciales'],
            'encryption': 'required_double',
            'access': 'privileged_only'
        }
    }
    
    def classify_data(self, data_type, content):
        """Clasificar datos automáticamente"""
        
        # Detectar PII
        if self.contains_pii(content):
            return 'restricted'
        
        # Detectar información financiera
        if self.contains_financial_data(content):
            return 'restricted'
        
        # Detectar datos de clientes
        if self.contains_customer_data(content):
            return 'confidential'
        
        # Default
        return 'internal'
```

### Encriptación de Datos

```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class DataEncryption:
    """Gestión de encriptación de datos"""
    
    def __init__(self):
        self.key_rotation_period = 90  # días
        self.encryption_keys = self.load_encryption_keys()
    
    def encrypt_sensitive_data(self, data, classification='confidential'):
        """Encriptar datos según su clasificación"""
        
        if classification == 'public':
            return data  # No requiere encriptación
        
        # Seleccionar algoritmo según clasificación
        if classification == 'restricted':
            # Doble encriptación para datos altamente sensibles
            encrypted = self.encrypt_aes256(data)
            encrypted = self.encrypt_rsa(encrypted)
            return encrypted
        else:
            # Encriptación estándar
            return self.encrypt_aes256(data)
    
    def encrypt_pii(self, pii_data):
        """Encriptación especial para PII"""
        
        # Tokenización primero
        tokenized = self.tokenize_data(pii_data)
        
        # Luego encriptación
        encrypted = self.encrypt_sensitive_data(tokenized, 'restricted')
        
        # Guardar mapeo token->encrypted en vault seguro
        self.store_in_vault(tokenized['token'], encrypted)
        
        return tokenized['token']
    
    def handle_key_rotation(self):
        """Rotar claves de encriptación"""
        
        if self.is_rotation_due():
            # Generar nueva clave
            new_key = self.generate_new_key()
            
            # Re-encriptar datos con nueva clave
            self.reencrypt_with_new_key(new_key)
            
            # Actualizar key store
            self.update_key_store(new_key)
            
            # Mantener clave antigua por período de gracia
            self.archive_old_key()
```

## 🔏 Autenticación y Autorización

### Sistema de Autenticación Multi-Factor

```python
class MultiFactorAuth:
    """Sistema de autenticación multi-factor"""
    
    def __init__(self):
        self.auth_methods = {
            'password': PasswordAuthenticator(),
            'otp': OTPAuthenticator(),
            'biometric': BiometricAuthenticator(),
            'push': PushNotificationAuthenticator()
        }
        
        self.risk_analyzer = RiskAnalyzer()
    
    def authenticate_user(self, credentials, context):
        """Autenticar usuario con MFA adaptativo"""
        
        # Analizar riesgo del contexto
        risk_score = self.risk_analyzer.analyze(context)
        
        # Determinar factores requeridos según riesgo
        required_factors = self.determine_required_factors(risk_score)
        
        # Verificar cada factor
        for factor in required_factors:
            if not self.verify_factor(factor, credentials):
                return {
                    'authenticated': False,
                    'failed_factor': factor,
                    'risk_score': risk_score
                }
        
        # Generar token de sesión
        session_token = self.generate_secure_token(credentials['user_id'])
        
        return {
            'authenticated': True,
            'session_token': session_token,
            'factors_used': required_factors,
            'expires_in': 3600
        }
    
    def determine_required_factors(self, risk_score):
        """Determinar factores según nivel de riesgo"""
        
        if risk_score < 0.3:
            return ['password']
        elif risk_score < 0.7:
            return ['password', 'otp']
        else:
            return ['password', 'otp', 'push']
```

### Control de Acceso Basado en Roles (RBAC)

```python
class RBACSystem:
    """Sistema de control de acceso basado en roles"""
    
    def __init__(self):
        self.roles = self.load_role_definitions()
        self.permissions = self.load_permission_matrix()
        self.user_assignments = {}
    
    def define_roles(self):
        """Definir roles del sistema"""
        
        return {
            'super_admin': {
                'permissions': ['*'],  # Todos los permisos
                'description': 'Administrador del sistema'
            },
            'ai_manager': {
                'permissions': [
                    'ai.view_all',
                    'ai.modify_config',
                    'ai.train_models',
                    'ai.view_analytics',
                    'knowledge_base.modify'
                ],
                'description': 'Gestor de AI Agents'
            },
            'conversation_analyst': {
                'permissions': [
                    'conversations.view_all',
                    'analytics.view',
                    'reports.generate',
                    'knowledge_base.view'
                ],
                'description': 'Analista de conversaciones'
            },
            'support_agent': {
                'permissions': [
                    'conversations.view_assigned',
                    'conversations.escalate',
                    'knowledge_base.view',
                    'users.view_basic'
                ],
                'description': 'Agente de soporte'
            },
            'api_consumer': {
                'permissions': [
                    'api.read',
                    'api.search_products',
                    'api.check_inventory'
                ],
                'description': 'Consumidor de API'
            }
        }
    
    def check_permission(self, user_id, resource, action):
        """Verificar si usuario tiene permiso"""
        
        # Obtener roles del usuario
        user_roles = self.get_user_roles(user_id)
        
        # Verificar cada rol
        for role in user_roles:
            if self.role_has_permission(role, resource, action):
                # Log acceso permitido
                self.audit_log.record({
                    'user_id': user_id,
                    'resource': resource,
                    'action': action,
                    'result': 'allowed',
                    'role': role
                })
                return True
        
        # Log acceso denegado
        self.audit_log.record({
            'user_id': user_id,
            'resource': resource,
            'action': action,
            'result': 'denied'
        })
        
        return False
```

## 📋 Cumplimiento Normativo

### GDPR Compliance

```python
class GDPRCompliance:
    """Gestión de cumplimiento GDPR"""
    
    def __init__(self):
        self.consent_manager = ConsentManager()
        self.data_processor = PersonalDataProcessor()
        self.rights_handler = DataSubjectRightsHandler()
    
    def handle_data_request(self, request_type, user_id):
        """Manejar solicitudes de derechos GDPR"""
        
        handlers = {
            'access': self.handle_access_request,
            'rectification': self.handle_rectification_request,
            'erasure': self.handle_erasure_request,
            'portability': self.handle_portability_request,
            'restriction': self.handle_restriction_request,
            'objection': self.handle_objection_request
        }
        
        handler = handlers.get(request_type)
        if not handler:
            raise ValueError(f"Unknown request type: {request_type}")
        
        # Verificar identidad
        if not self.verify_identity(user_id):
            return {'error': 'Identity verification failed'}
        
        # Procesar solicitud
        result = handler(user_id)
        
        # Registrar en audit log
        self.audit_log.record_gdpr_request({
            'user_id': user_id,
            'request_type': request_type,
            'timestamp': datetime.now(),
            'result': result['status']
        })
        
        return result
    
    def handle_erasure_request(self, user_id):
        """Derecho al olvido"""
        
        # Verificar si hay obligaciones legales de retención
        if self.has_legal_retention_obligation(user_id):
            return {
                'status': 'partial',
                'message': 'Some data must be retained for legal reasons',
                'retained_data': self.get_legally_required_data(user_id)
            }
        
        # Proceder con eliminación
        deletion_plan = self.create_deletion_plan(user_id)
        
        # Ejecutar eliminación
        for system in deletion_plan['systems']:
            self.delete_from_system(system, user_id)
        
        # Notificar a terceros
        self.notify_third_parties(user_id, 'erasure')
        
        return {
            'status': 'completed',
            'deleted_from': deletion_plan['systems'],
            'completion_date': datetime.now()
        }
```

### Ley de Protección de Datos Colombia

```python
class ColombianDataProtection:
    """Cumplimiento Ley 1581 de 2012 - Colombia"""
    
    def __init__(self):
        self.habeas_data_registry = HabeasDataRegistry()
        self.sic_reporter = SICReporter()  # Superintendencia de Industria y Comercio
    
    def ensure_compliance(self):
        """Asegurar cumplimiento con ley colombiana"""
        
        compliance_checks = {
            'privacy_policy': self.verify_privacy_policy(),
            'consent_mechanism': self.verify_consent_mechanism(),
            'data_treatment': self.verify_data_treatment(),
            'security_measures': self.verify_security_measures(),
            'breach_notification': self.verify_breach_procedure(),
            'registry_updated': self.verify_registry_status()
        }
        
        non_compliant = [
            check for check, status in compliance_checks.items()
            if not status
        ]
        
        if non_compliant:
            self.generate_compliance_report(non_compliant)
            self.create_remediation_plan(non_compliant)
        
        return compliance_checks
    
    def register_database(self):
        """Registrar base de datos ante RNBD"""
        
        registration = {
            'company': 'KOAJ',
            'database_name': 'Customer Engagement Database',
            'purpose': 'E-commerce y atención al cliente',
            'data_categories': [
                'Identificación',
                'Ubicación',
                'Comerciales',
                'Transaccionales'
            ],
            'security_measures': self.list_security_measures(),
            'retention_period': '10 años',
            'international_transfers': False
        }
        
        return self.habeas_data_registry.register(registration)
```

## 🔍 Auditoría y Logging

### Sistema de Auditoría Inmutable

```python
import hashlib
from datetime import datetime

class ImmutableAuditLog:
    """Log de auditoría inmutable con blockchain"""
    
    def __init__(self):
        self.blockchain = []
        self.current_block = []
        self.block_size = 1000
    
    def log_event(self, event):
        """Registrar evento en log inmutable"""
        
        # Crear entrada de log
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event['type'],
            'user_id': event.get('user_id'),
            'ip_address': event.get('ip_address'),
            'action': event['action'],
            'resource': event.get('resource'),
            'result': event['result'],
            'metadata': event.get('metadata', {})
        }
        
        # Agregar hash del evento
        log_entry['hash'] = self.calculate_hash(log_entry)
        
        # Agregar al bloque actual
        self.current_block.append(log_entry)
        
        # Si el bloque está lleno, sellarlo
        if len(self.current_block) >= self.block_size:
            self.seal_block()
        
        return log_entry['hash']
    
    def seal_block(self):
        """Sellar bloque actual y agregarlo a la cadena"""
        
        block = {
            'index': len(self.blockchain),
            'timestamp': datetime.now().isoformat(),
            'entries': self.current_block,
            'previous_hash': self.get_previous_hash(),
            'nonce': 0
        }
        
        # Proof of work simple
        block['hash'] = self.mine_block(block)
        
        # Agregar a blockchain
        self.blockchain.append(block)
        
        # Reiniciar bloque actual
        self.current_block = []
        
        # Replicar a almacenamiento inmutable
        self.replicate_to_storage(block)
```

### Detección de Anomalías

```python
class AnomalyDetection:
    """Sistema de detección de anomalías en seguridad"""
    
    def __init__(self):
        self.ml_model = self.load_anomaly_model()
        self.baseline_behavior = {}
        self.alert_threshold = 0.95
    
    def analyze_user_behavior(self, user_id, action_sequence):
        """Analizar comportamiento del usuario"""
        
        # Obtener baseline del usuario
        baseline = self.baseline_behavior.get(user_id)
        
        if not baseline:
            # Nuevo usuario, establecer baseline
            self.establish_baseline(user_id, action_sequence)
            return {'anomaly_score': 0, 'is_anomaly': False}
        
        # Calcular score de anomalía
        features = self.extract_features(action_sequence)
        anomaly_score = self.ml_model.predict_anomaly(features, baseline)
        
        # Determinar si es anomalía
        is_anomaly = anomaly_score > self.alert_threshold
        
        if is_anomaly:
            self.handle_anomaly({
                'user_id': user_id,
                'score': anomaly_score,
                'actions': action_sequence,
                'timestamp': datetime.now()
            })
        
        return {
            'anomaly_score': anomaly_score,
            'is_anomaly': is_anomaly,
            'risk_level': self.calculate_risk_level(anomaly_score)
        }
```

## 🚨 Incident Response

### Plan de Respuesta a Incidentes

```python
class IncidentResponsePlan:
    """Plan de respuesta a incidentes de seguridad"""
    
    def __init__(self):
        self.incident_levels = {
            'low': {'response_time': '24h', 'team': 'security_analyst'},
            'medium': {'response_time': '4h', 'team': 'security_team'},
            'high': {'response_time': '1h', 'team': 'incident_response_team'},
            'critical': {'response_time': '15m', 'team': 'crisis_management'}
        }
        
        self.playbooks = self.load_playbooks()
    
    def handle_security_incident(self, incident):
        """Manejar incidente de seguridad"""
        
        # Clasificar incidente
        severity = self.classify_incident(incident)
        
        # Iniciar respuesta
        response = {
            'incident_id': self.generate_incident_id(),
            'severity': severity,
            'started_at': datetime.now(),
            'status': 'responding',
            'actions': []
        }
        
        # Ejecutar playbook
        playbook = self.playbooks[incident['type']]
        
        for step in playbook['steps']:
            result = self.execute_step(step, incident)
            response['actions'].append({
                'step': step['name'],
                'result': result,
                'timestamp': datetime.now()
            })
            
            if step.get('notify'):
                self.notify_stakeholders(step['notify'], incident, result)
        
        # Contención
        if severity in ['high', 'critical']:
            self.contain_threat(incident)
        
        # Investigación
        investigation = self.investigate_incident(incident)
        response['investigation'] = investigation
        
        # Remediación
        remediation = self.remediate_incident(incident, investigation)
        response['remediation'] = remediation
        
        # Lecciones aprendidas
        self.document_lessons_learned(response)
        
        return response
```

### Gestión de Vulnerabilidades

```python
class VulnerabilityManagement:
    """Sistema de gestión de vulnerabilidades"""
    
    def __init__(self):
        self.scanner = VulnerabilityScanner()
        self.patch_manager = PatchManager()
        self.risk_calculator = RiskCalculator()
    
    async def scan_infrastructure(self):
        """Escanear infraestructura en busca de vulnerabilidades"""
        
        scan_results = {
            'scan_id': self.generate_scan_id(),
            'timestamp': datetime.now(),
            'vulnerabilities': []
        }
        
        # Escanear diferentes componentes
        components = [
            'web_application',
            'api_endpoints',
            'databases',
            'network_infrastructure',
            'dependencies'
        ]
        
        for component in components:
            vulns = await self.scanner.scan_component(component)
            
            for vuln in vulns:
                # Calcular riesgo
                risk_score = self.risk_calculator.calculate(vuln)
                
                scan_results['vulnerabilities'].append({
                    'component': component,
                    'vulnerability': vuln,
                    'risk_score': risk_score,
                    'remediation': self.get_remediation_plan(vuln)
                })
        
        # Priorizar remediación
        scan_results['priority_order'] = self.prioritize_remediation(
            scan_results['vulnerabilities']
        )
        
        # Crear tickets de remediación
        self.create_remediation_tickets(scan_results)
        
        return scan_results
```

## 🔐 Gestión de Secretos

### Vault de Secretos

```python
class SecretVault:
    """Gestión segura de secretos y credenciales"""
    
    def __init__(self):
        self.vault_client = self.initialize_vault()
        self.encryption_key = self.get_master_key()
        self.access_policies = self.load_access_policies()
    
    def store_secret(self, secret_name, secret_value, metadata=None):
        """Almacenar secreto de forma segura"""
        
        # Validar permisos
        if not self.check_write_permission():
            raise PermissionError("No write permission to vault")
        
        # Encriptar secreto
        encrypted_value = self.encrypt_secret(secret_value)
        
        # Preparar metadata
        secret_metadata = {
            'created_by': self.get_current_user(),
            'created_at': datetime.now(),
            'classification': self.classify_secret(secret_name),
            'rotation_policy': self.get_rotation_policy(secret_name),
            'access_policy': self.get_access_policy(secret_name)
        }
        
        if metadata:
            secret_metadata.update(metadata)
        
        # Almacenar en vault
        self.vault_client.write(
            path=f"secret/{secret_name}",
            data={
                'value': encrypted_value,
                'metadata': secret_metadata
            }
        )
        
        # Audit log
        self.audit_log.record_secret_access({
            'action': 'create',
            'secret_name': secret_name,
            'user': self.get_current_user(),
            'timestamp': datetime.now()
        })
        
        return True
    
    def rotate_secrets(self):
        """Rotar secretos según política"""
        
        secrets_to_rotate = self.get_secrets_due_for_rotation()
        
        rotation_results = []
        for secret in secrets_to_rotate:
            try:
                # Generar nuevo secreto
                new_value = self.generate_new_secret(secret['type'])
                
                # Actualizar en sistemas dependientes
                self.update_dependent_systems(secret['name'], new_value)
                
                # Actualizar en vault
                self.update_secret(secret['name'], new_value)
                
                rotation_results.append({
                    'secret': secret['name'],
                    'status': 'success',
                    'rotated_at': datetime.now()
                })
                
            except Exception as e:
                rotation_results.append({
                    'secret': secret['name'],
                    'status': 'failed',
                    'error': str(e)
                })
                
                # Alertar al equipo de seguridad
                self.alert_security_team(f"Secret rotation failed: {secret['name']}")
        
        return rotation_results
```

## 🛡️ Protección contra Ataques

### WAF y Protección DDoS

```python
class SecurityProtection:
    """Protección contra ataques comunes"""
    
    def __init__(self):
        self.waf_rules = self.load_waf_rules()
        self.ddos_mitigation = DDoSMitigation()
        self.threat_intelligence = ThreatIntelligence()
    
    def protect_against_injection(self, request):
        """Protección contra inyección SQL/NoSQL"""
        
        # Patrones de inyección conocidos
        injection_patterns = [
            r"('\s*OR\s*'1'\s*=\s*'1)",  # SQL injection
            r"(;\s*DROP\s+TABLE)",         # SQL injection
            r"(\$where|\$ne|\$gt)",        # NoSQL injection
            r"(<script[^>]*>.*?</script>)", # XSS
            r"(javascript:)",              # XSS
            r"(\.\./){2,}",               # Path traversal
        ]
        
        # Verificar cada patrón
        for pattern in injection_patterns:
            if re.search(pattern, str(request), re.IGNORECASE):
                # Log intento de ataque
                self.log_attack_attempt({
                    'type': 'injection',
                    'pattern': pattern,
                    'request': request,
                    'ip': request.get('ip_address'),
                    'timestamp': datetime.now()
                })
                
                # Bloquear request
                return {
                    'blocked': True,
                    'reason': 'Potential injection attack detected'
                }
        
        return {'blocked': False}
    
    def implement_rate_limiting(self):
        """Implementar rate limiting por IP/Usuario"""
        
        rate_limits = {
            'global': {'requests': 1000, 'window': 60},      # 1000 req/min global
            'per_ip': {'requests': 100, 'window': 60},       # 100 req/min por IP
            'per_user': {'requests': 300, 'window': 60},     # 300 req/min por usuario
            'api_endpoints': {
                '/bird/ai-search': {'requests': 30, 'window': 60},
                '/products': {'requests': 100, 'window': 60},
                '/auth/login': {'requests': 5, 'window': 300}    # 5 intentos/5min
            }
        }
        
        return RateLimiter(rate_limits)
```

## 📊 Métricas de Seguridad

### Dashboard de Seguridad

```python
class SecurityDashboard:
    """Dashboard de métricas de seguridad"""
    
    def get_security_metrics(self):
        """Obtener métricas de seguridad en tiempo real"""
        
        return {
            'threat_indicators': {
                'blocked_requests_24h': self.count_blocked_requests(hours=24),
                'failed_auth_attempts': self.count_failed_auth(hours=24),
                'anomalies_detected': self.count_anomalies(hours=24),
                'active_incidents': self.get_active_incidents()
            },
            
            'compliance_status': {
                'gdpr': self.check_gdpr_compliance(),
                'colombian_law': self.check_colombian_compliance(),
                'pci_dss': self.check_pci_compliance(),
                'last_audit': self.get_last_audit_date()
            },
            
            'vulnerability_status': {
                'critical_vulns': self.count_vulnerabilities('critical'),
                'high_vulns': self.count_vulnerabilities('high'),
                'last_scan': self.get_last_scan_date(),
                'patch_compliance': self.calculate_patch_compliance()
            },
            
            'access_control': {
                'active_sessions': self.count_active_sessions(),
                'privileged_users': self.count_privileged_users(),
                'mfa_adoption': self.calculate_mfa_adoption(),
                'api_key_rotation': self.check_api_key_age()
            }
        }
```

## 🎯 Próximos Pasos

Con la seguridad implementada:

1. **[Troubleshooting](troubleshooting.md)** - Resolver problemas de seguridad
3. **[templates/](templates/)** - Templates de políticas de seguridad

---

**Recuerda**: La seguridad no es un producto, es un proceso. Requiere vigilancia constante, actualización continua y una cultura de seguridad en toda la organización. Un sistema es tan seguro como su eslabón más débil.