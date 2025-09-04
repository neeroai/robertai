# Plan de Recuperación de Desastres - RobertAI Masivo
## Guía Completa para Manejo de Emergencias y Failover

### Resumen Ejecutivo

Este documento establece los procedimientos completos de recuperación de desastres para el **despliegue masivo de RobertAI**, diseñado para manejar **5,000-10,000 usuarios concurrentes** en WhatsApp a través de Bird.com. El sistema incluye mecanismos automáticos de failover, procedimientos de rollback y respuesta de emergencia para garantizar máxima disponibilidad durante la "prueba de fuego" masiva.

---

## 📋 Tabla de Contenidos

1. [Arquitectura de Failover](#arquitectura-de-failover)
2. [Niveles de Severidad](#niveles-de-severidad)  
3. [Procedimientos de Emergencia](#procedimientos-de-emergencia)
4. [Monitoreo y Alertas](#monitoreo-y-alertas)
5. [Rollback y Recuperación](#rollback-y-recuperación)
6. [Contactos de Emergencia](#contactos-de-emergencia)
7. [Runbooks Operacionales](#runbooks-operacionales)

---

## 🏗️ Arquitectura de Failover

### Componentes Críticos

#### 1. Load Balancer (Crítico)
- **Endpoint**: `http://localhost:8000/health/load-balancer`
- **Función**: Distribución de carga entre múltiples números de WhatsApp
- **Failover**: Activación automática de números backup
- **SLA**: < 3 segundos de downtime

#### 2. Queue Processor (Crítico)
- **Endpoint**: `http://localhost:8001/health`  
- **Función**: Procesamiento de miles de mensajes concurrentes
- **Failover**: Workers de backup + escalado automático
- **SLA**: < 5 segundos de downtime

#### 3. Cache System (Crítico)
- **Endpoint**: `http://localhost:8002/health`
- **Función**: Cache multicapa para optimización de rendimiento
- **Failover**: Redis cluster backup + invalidación inteligente
- **SLA**: < 2 segundos de downtime

#### 4. Database Cluster (Crítico)  
- **Endpoint**: `http://localhost:8000/health/database`
- **Función**: Persistencia de datos y estado de conversaciones
- **Failover**: Read replicas + snapshots automáticos
- **SLA**: < 10 segundos de downtime

---

## 🚨 Niveles de Severidad

### Nivel 1: HEALTHY 🟢
- **Estado**: Todos los servicios operacionales
- **Acción**: Monitoreo continuo
- **Notificación**: Logs normales

### Nivel 2: DEGRADED 🟡
- **Estado**: 1-2 servicios no críticos afectados
- **Acción**: Degradación gradual automática
- **Notificación**: Alertas por Slack
- **Ejemplo**: Monitoring dashboard offline

### Nivel 3: CRITICAL 🟠  
- **Estado**: 1 servicio crítico fallando
- **Acción**: Failover automático activado
- **Notificación**: Alertas por Slack + Email
- **Ejemplo**: Database connection intermittente

### Nivel 4: EMERGENCY 🔴
- **Estado**: 2+ servicios críticos fallando
- **Acción**: Respuesta de emergencia completa
- **Notificación**: Slack + Email + SMS + PagerDuty
- **Ejemplo**: Load balancer + Queue processor offline

---

## ⚡ Procedimientos de Emergencia

### Activación Automática de Failover

El sistema **EmergencyFailoverSystem** monitorea continuamente y activa respuestas automáticas:

```bash
# Iniciar monitoring continuo
python3 services/emergency_failover.py

# O usar el script de emergencia
./scripts/emergency_procedures.sh monitor
```

### Secuencias de Failover por Nivel

#### Degradación Gradual (Nivel 2)
```yaml
acciones:
  - reducir_rate_limits: 70%
  - deshabilitar_features_no_esenciales: true
  - aumentar_cache_ttl: 300s
  - modo_cola_prioritaria: true
```

#### Failover Crítico (Nivel 3)
```yaml
secuencia:
  1. restart_servicio_fallido (120s timeout)
  2. escalar_infraestructura (+30% instancias)  
  3. activar_numeros_backup_whatsapp
  4. limpiar_cache_problematico
  5. validar_recuperacion (180s)
```

#### Respuesta de Emergencia (Nivel 4)
```yaml
secuencia:
  1. snapshot_emergencia_completo
  2. escalar_infraestructura (+100% instancias)
  3. activar_todos_los_backups
  4. modo_mantenimiento_temporal
  5. notificar_todos_los_contactos
```

---

## 📊 Monitoreo y Alertas

### Health Checks Configurados

#### Servicios Críticos (cada 10-15s)
- **Load Balancer**: `/health/load-balancer` 
- **Queue Processor**: `/health`
- **Cache System**: `/health` 
- **Database**: `/health/database`
- **WhatsApp Webhook**: `/webhooks/whatsapp/health`

#### Servicios No Críticos (cada 60-180s)
- **Monitoring Dashboard**: `/health`
- **Analytics Service**: `/health`  
- **Bird API Integration**: `https://api.bird.com/health`

### Umbrales de Performance

#### Tiempo de Respuesta
- **Warning**: > 1000ms
- **Critical**: > 3000ms  
- **Emergency**: > 5000ms

#### Tasa de Éxito
- **Warning**: < 95%
- **Critical**: < 90%
- **Emergency**: < 85%

#### Throughput (Mensajes/Segundo)
- **Warning**: < 500 msg/s
- **Critical**: < 200 msg/s
- **Emergency**: < 100 msg/s

---

## 🔄 Rollback y Recuperación

### Sistema de Snapshots Automáticos

El sistema crea snapshots cada 5 minutos conteniendo:

- **Estado de Base de Datos**: RDS snapshot automático
- **Versión de Aplicación**: Git commit hash
- **Estado de Infraestructura**: Configuración AWS
- **Estado de Cache**: Configuración Redis
- **Configuración Load Balancer**: Números WhatsApp activos

### Procedimientos de Rollback

#### Rollback de Aplicación
```bash
# Listar snapshots disponibles
./scripts/emergency_procedures.sh status

# Rollback a snapshot específico  
./scripts/emergency_procedures.sh rollback emergency_20240304_142030
```

#### Rollback de Base de Datos
```bash
# Rollback automático incluido en rollback completo
./scripts/emergency_procedures.sh rollback emergency_20240304_142030

# O rollback manual de RDS
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier robertai-db-restored \
  --db-snapshot-identifier emergency_20240304_142030_db
```

### Tiempo de Recuperación Objetivo (RTO)

- **Aplicación**: < 5 minutos
- **Base de Datos**: < 15 minutos  
- **Infraestructura**: < 10 minutos
- **Sistema Completo**: < 20 minutos

### Punto de Recuperación Objetivo (RPO)

- **Transacciones**: < 1 minuto
- **Configuración**: < 5 minutos
- **Snapshots**: < 5 minutos

---

## 📞 Contactos de Emergencia

### Escalation Matrix

#### Nivel 1 - Operations Team
- **Slack**: `#robertai-emergencies`
- **Webhook**: `${SLACK_WEBHOOK_URL}`
- **Respuesta**: < 5 minutos

#### Nivel 2 - Technical Lead  
- **Email**: `tech-lead@company.com`
- **Teléfono**: `+1-XXX-XXX-XXXX`
- **Respuesta**: < 15 minutos

#### Nivel 3 - On-call Engineer
- **SMS**: `${ONCALL_PHONE}`  
- **PagerDuty**: `${PAGERDUTY_KEY}`
- **Respuesta**: < 10 minutos

#### Nivel 4 - Management Escalation
- **Email**: `management@company.com`
- **Respuesta**: < 30 minutos

---

## 📖 Runbooks Operacionales

### Runbook 1: Service Restart Failure

**Síntoma**: Servicio no se reinicia después de fallo
**Procedimiento**:
1. Verificar logs: `journalctl -u robertai-<service> -f`
2. Verificar dependencias: `systemctl list-dependencies robertai-<service>`  
3. Reinicio manual: `systemctl reset-failed robertai-<service>`
4. Si falla: Activar backup y escalar
5. Documentar en incident tracker

### Runbook 2: Database Connection Loss

**Síntoma**: Conexiones a base de datos fallan
**Procedimiento**:
1. Verificar RDS status en AWS Console
2. Verificar security groups y NACLs
3. Restart connection pools: `systemctl restart robertai-*`
4. Si persiste: Activar read replicas
5. Considerar failover de RDS

### Runbook 3: Mass WhatsApp Rate Limiting  

**Síntoma**: Múltiples números WhatsApp siendo rate-limited
**Procedimiento**:
1. Activar números backup: `./scripts/emergency_procedures.sh activate-backup`
2. Redistribuir carga: Actualizar load balancer weights
3. Verificar con Bird.com API status
4. Implementar backoff exponencial
5. Escalar números WhatsApp si necesario

### Runbook 4: Cache Cluster Failure

**Síntoma**: Redis cluster no responde
**Procedimiento**:
1. Verificar ElastiCache cluster status
2. Activar backup Redis: Configurado en failover_config.yaml  
3. Limpiar cache corrupto: `redis-cli flushdb`
4. Reiniciar aplicaciones para reconectar
5. Monitorear performance sin cache

### Runbook 5: Auto Scaling Failure

**Síntoma**: Instancias EC2 no escalan automáticamente  
**Procedimiento**:
1. Verificar ASG limits y policies
2. Verificar IAM permissions para ASG
3. Scaling manual: `./scripts/emergency_procedures.sh scale-up 30`
4. Verificar launch template y AMI
5. Considerar scaling en otra AZ

---

## 🧪 Pruebas de Disaster Recovery

### Pruebas Programadas

#### Monthly Chaos Testing
- **Fecha**: Primer domingo de cada mes
- **Horario**: 02:00-04:00 UTC (ventana de mantenimiento)
- **Procedimiento**: Fallo simulado de servicios individuales

#### Quarterly Full DR Test  
- **Fecha**: Cada trimestre
- **Horario**: 4 horas durante ventana de mantenimiento
- **Procedimiento**: Rollback completo a snapshot anterior

### Métricas de Éxito para Pruebas

- **RTO Achieved**: < tiempo objetivo definido
- **RPO Achieved**: < tiempo objetivo definido  
- **Data Integrity**: 100% de datos recuperados
- **Service Recovery**: Todos los servicios operacionales
- **Notification System**: Todas las alertas funcionando

---

## 📈 Métricas y KPIs

### Disponibilidad del Sistema
- **Target**: 99.9% uptime (8.76 horas downtime/año)
- **Measurement**: Synthetic checks cada minuto
- **Reporting**: Dashboard en tiempo real

### Performance Durante Failover
- **Message Processing**: Mantener > 500 msg/s
- **Response Time**: < 3s durante failover
- **Success Rate**: > 95% durante failover

### Recovery Metrics
- **MTTR** (Mean Time To Recovery): < 20 minutos
- **MTBF** (Mean Time Between Failures): > 30 días  
- **False Positive Rate**: < 5% de alertas

---

## 🔐 Seguridad Durante Emergencias

### Acceso de Emergencia
- **Temporary Tokens**: 1 hora de duración
- **MFA Required**: Siempre habilitado
- **Audit Logging**: Todas las acciones registradas

### Data Protection  
- **Encryption**: AES-256 at rest, TLS 1.3 in transit
- **Backup Security**: Snapshots encriptados
- **Access Control**: Principle of least privilege

---

## 📋 Checklist de Post-Incident

### Immediate (0-2 hours)
- [ ] Sistema completamente restaurado
- [ ] All services health = GREEN
- [ ] Performance metrics = baseline
- [ ] Stakeholders notificados de resolución

### Short-term (2-24 hours)  
- [ ] Incident report preliminar
- [ ] Root cause análisis iniciado
- [ ] Temporary fixes documentados
- [ ] Customer communication sent

### Long-term (1-7 days)
- [ ] Full post-mortem completado
- [ ] Process improvements identificados  
- [ ] System hardening implementado
- [ ] Runbook updates realizados
- [ ] Team training programado

---

## 📚 Referencias y Documentación

### Scripts y Herramientas
- **Emergency Procedures**: `./scripts/emergency_procedures.sh`
- **Failover System**: `./services/emergency_failover.py`
- **Configuration**: `./config/failover_config.yaml`
- **Monitoring**: `./services/real_time_monitoring.py`

### Documentación Relacionada
- **Load Balancer**: `./services/load_balancer.py`
- **Cache Strategy**: `./services/massive_cache.py` 
- **Queue Processing**: `./services/massive_queue_processor.py`
- **AWS Infrastructure**: `./config/aws_infrastructure.yaml`
- **Stress Testing**: `./tests/stress_test_massive.py`

### External Dependencies
- **AWS Services**: RDS, ElastiCache, ALB, ASG, CloudWatch
- **Bird.com API**: WhatsApp Business API integration
- **Monitoring Tools**: Prometheus, Grafana, PagerDuty

---

## ⚠️ Contacto de Emergencia 24/7

**Para emergencias críticas que requieren intervención inmediata:**

🔴 **EMERGENCY HOTLINE**: `+1-XXX-XXX-XXXX`  
📧 **EMERGENCY EMAIL**: `emergency@company.com`  
💬 **SLACK EMERGENCY**: `#robertai-critical-alerts`

**Este documento debe ser actualizado después de cada incidente y revisado mensualmente.**

---
*Última actualización: $(date)*
*Versión: 1.0*
*Propietario: Technical Operations Team*