#!/bin/bash

# Emergency Procedures Script for RobertAI Massive Deployment
# Comprehensive emergency response procedures for handling thousands of concurrent users

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
CONFIG_FILE="${PROJECT_ROOT}/config/failover_config.yaml"
LOG_FILE="/var/log/robertai/emergency.log"
PIDFILE="/var/run/robertai/emergency_monitor.pid"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

error() {
    log "${RED}ERROR: $1${NC}"
}

warn() {
    log "${YELLOW}WARNING: $1${NC}"
}

info() {
    log "${BLUE}INFO: $1${NC}"
}

success() {
    log "${GREEN}SUCCESS: $1${NC}"
}

# Check if running as root for system operations
check_root() {
    if [[ $EUID -eq 0 ]]; then
        warn "Running as root. This may be necessary for system operations."
    fi
}

# Validate environment
validate_environment() {
    info "Validating emergency environment..."
    
    # Check required tools
    local required_tools=("docker" "aws" "kubectl" "systemctl" "redis-cli" "psql")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            error "Required tool not found: $tool"
            exit 1
        fi
    done
    
    # Check configuration file
    if [[ ! -f "$CONFIG_FILE" ]]; then
        error "Configuration file not found: $CONFIG_FILE"
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        error "AWS credentials not configured or expired"
        exit 1
    fi
    
    # Check log directory
    mkdir -p "$(dirname "$LOG_FILE")"
    mkdir -p "$(dirname "$PIDFILE")"
    
    success "Environment validation completed"
}

# Get system status
get_system_status() {
    info "Getting current system status..."
    
    echo "=== RobertAI System Status ==="
    echo "Timestamp: $(date)"
    echo
    
    # Service status
    echo "=== Service Status ==="
    local services=("robertai-load-balancer" "robertai-queue-processor" "robertai-cache" "robertai-monitoring")
    for service in "${services[@]}"; do
        if systemctl is-active --quiet "$service"; then
            echo -e "  $service: ${GREEN}RUNNING${NC}"
        else
            echo -e "  $service: ${RED}STOPPED${NC}"
        fi
    done
    echo
    
    # AWS Auto Scaling status
    echo "=== AWS Auto Scaling Status ==="
    local asg_name=$(yq eval '.aws.auto_scaling_group' "$CONFIG_FILE")
    if [[ -n "$asg_name" ]]; then
        aws autoscaling describe-auto-scaling-groups \
            --auto-scaling-group-names "$asg_name" \
            --query 'AutoScalingGroups[0].{DesiredCapacity:DesiredCapacity,MinSize:MinSize,MaxSize:MaxSize,Instances:Instances[].{Id:InstanceId,State:LifecycleState,Health:HealthStatus}}' \
            --output table
    fi
    echo
    
    # Load balancer status
    echo "=== Load Balancer Status ==="
    if command -v curl &> /dev/null; then
        local response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health || echo "000")
        if [[ "$response" == "200" ]]; then
            echo -e "  Load Balancer: ${GREEN}HEALTHY${NC}"
        else
            echo -e "  Load Balancer: ${RED}UNHEALTHY (HTTP $response)${NC}"
        fi
    fi
    echo
    
    # Database status
    echo "=== Database Status ==="
    if command -v redis-cli &> /dev/null; then
        if redis-cli ping &> /dev/null; then
            echo -e "  Redis Cache: ${GREEN}CONNECTED${NC}"
        else
            echo -e "  Redis Cache: ${RED}DISCONNECTED${NC}"
        fi
    fi
    echo
    
    # Queue status
    echo "=== Queue Status ==="
    if [[ -f "/tmp/robertai_queue_stats.json" ]]; then
        echo "  Queue Stats:"
        cat /tmp/robertai_queue_stats.json | jq .
    else
        echo "  Queue stats not available"
    fi
}

# Emergency scale up
emergency_scale_up() {
    local target_instances=${1:-20}
    info "Initiating emergency scale up to $target_instances instances..."
    
    local asg_name=$(yq eval '.aws.auto_scaling_group' "$CONFIG_FILE")
    if [[ -z "$asg_name" ]]; then
        error "Auto Scaling Group name not found in configuration"
        return 1
    fi
    
    # Get current capacity
    local current_capacity=$(aws autoscaling describe-auto-scaling-groups \
        --auto-scaling-group-names "$asg_name" \
        --query 'AutoScalingGroups[0].DesiredCapacity' \
        --output text)
    
    info "Current capacity: $current_capacity, Target: $target_instances"
    
    if [[ "$current_capacity" -lt "$target_instances" ]]; then
        # Update Auto Scaling Group
        aws autoscaling update-auto-scaling-group \
            --auto-scaling-group-name "$asg_name" \
            --desired-capacity "$target_instances" \
            --max-size "$((target_instances + 10))"
        
        success "Emergency scale up initiated to $target_instances instances"
        
        # Wait for instances to be ready
        info "Waiting for instances to become ready..."
        for i in {1..10}; do
            local ready_instances=$(aws autoscaling describe-auto-scaling-groups \
                --auto-scaling-group-names "$asg_name" \
                --query 'AutoScalingGroups[0].Instances[?LifecycleState==`InService`]' \
                --output json | jq length)
            
            info "Ready instances: $ready_instances/$target_instances"
            
            if [[ "$ready_instances" -ge "$target_instances" ]]; then
                success "All instances are ready"
                break
            fi
            
            sleep 30
        done
    else
        info "System already scaled to desired level"
    fi
}

# Restart failed services
restart_failed_services() {
    info "Restarting failed services..."
    
    local services=("robertai-load-balancer" "robertai-queue-processor" "robertai-cache" "robertai-monitoring")
    local restarted_services=()
    
    for service in "${services[@]}"; do
        if ! systemctl is-active --quiet "$service"; then
            warn "Restarting failed service: $service"
            
            if systemctl restart "$service"; then
                success "Successfully restarted: $service"
                restarted_services+=("$service")
            else
                error "Failed to restart: $service"
            fi
            
            # Wait a moment between restarts
            sleep 5
        else
            info "Service already running: $service"
        fi
    done
    
    if [[ ${#restarted_services[@]} -gt 0 ]]; then
        info "Restarted services: ${restarted_services[*]}"
        
        # Wait for services to stabilize
        info "Waiting for services to stabilize..."
        sleep 30
        
        # Validate services are healthy
        for service in "${restarted_services[@]}"; do
            if systemctl is-active --quiet "$service"; then
                success "Service stable: $service"
            else
                error "Service unstable after restart: $service"
            fi
        done
    else
        info "No services needed restart"
    fi
}

# Activate backup systems
activate_backup_systems() {
    info "Activating backup systems..."
    
    # Activate backup Redis instance
    local backup_redis_host=$(yq eval '.redis.backup.host' "$CONFIG_FILE")
    if [[ -n "$backup_redis_host" && "$backup_redis_host" != "null" ]]; then
        info "Switching to backup Redis instance..."
        
        # Update load balancer configuration
        redis-cli hset load_balancer:config backup_mode true
        redis-cli hset load_balancer:config backup_redis_host "$backup_redis_host"
        redis-cli hset load_balancer:config failover_timestamp "$(date -Iseconds)"
        
        success "Activated backup Redis instance"
    fi
    
    # Activate backup WhatsApp numbers
    info "Activating backup WhatsApp numbers..."
    redis-cli hset load_balancer:config use_backup_numbers true
    
    # Scale up backup infrastructure
    local backup_asg="robertai-backup-asg"
    if aws autoscaling describe-auto-scaling-groups --auto-scaling-group-names "$backup_asg" &> /dev/null; then
        aws autoscaling update-auto-scaling-group \
            --auto-scaling-group-name "$backup_asg" \
            --desired-capacity 5 \
            --min-size 2 \
            --max-size 20
        
        success "Scaled up backup infrastructure"
    fi
}

# Enable graceful degradation
enable_graceful_degradation() {
    info "Enabling graceful degradation mode..."
    
    local degradation_config='{
        "enabled": true,
        "timestamp": "'$(date -Iseconds)'",
        "rate_limit_factor": 0.7,
        "cache_ttl_factor": 1.5,
        "disable_features": ["analytics", "detailed_logging", "background_sync", "image_processing"],
        "queue_priority_only": true,
        "reduce_worker_pools": true
    }'
    
    # Store degradation config in Redis
    redis-cli hset system:degradation config "$degradation_config"
    redis-cli expire system:degradation 3600  # Expire in 1 hour
    
    # Restart services to apply degradation
    systemctl reload robertai-load-balancer
    systemctl reload robertai-queue-processor
    
    success "Graceful degradation enabled"
    info "Features disabled: analytics, detailed_logging, background_sync, image_processing"
    info "Rate limiting reduced to 70% of normal capacity"
    info "Cache TTL increased by 50%"
}

# Create emergency snapshot
create_emergency_snapshot() {
    local reason=${1:-"manual_emergency_snapshot"}
    info "Creating emergency system snapshot..."
    
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local snapshot_id="emergency_${timestamp}"
    
    # Database snapshot
    local rds_instance=$(yq eval '.aws.rds_instance' "$CONFIG_FILE")
    if [[ -n "$rds_instance" && "$rds_instance" != "null" ]]; then
        info "Creating RDS snapshot..."
        aws rds create-db-snapshot \
            --db-instance-identifier "$rds_instance" \
            --db-snapshot-identifier "${snapshot_id}_db" &
        
        local db_snapshot_pid=$!
    fi
    
    # Application snapshot (Git commit)
    info "Creating application snapshot..."
    local git_commit=$(git rev-parse HEAD)
    echo "$git_commit" > "/tmp/emergency_snapshot_${timestamp}_git.txt"
    
    # Configuration snapshot
    info "Creating configuration snapshot..."
    cp -r "${PROJECT_ROOT}/config" "/tmp/emergency_snapshot_${timestamp}_config/"
    
    # Redis snapshot
    info "Creating Redis snapshot..."
    redis-cli bgsave
    
    # System state snapshot
    info "Capturing system state..."
    {
        echo "=== Emergency Snapshot: $snapshot_id ==="
        echo "Timestamp: $(date -Iseconds)"
        echo "Reason: $reason"
        echo "Git Commit: $git_commit"
        echo
        get_system_status
    } > "/tmp/emergency_snapshot_${timestamp}_system.txt"
    
    # Wait for database snapshot if started
    if [[ -n "${db_snapshot_pid:-}" ]]; then
        info "Waiting for database snapshot to complete..."
        wait $db_snapshot_pid
    fi
    
    # Store snapshot metadata in Redis
    local snapshot_metadata='{
        "snapshot_id": "'$snapshot_id'",
        "timestamp": "'$(date -Iseconds)'",
        "reason": "'$reason'",
        "git_commit": "'$git_commit'",
        "files": {
            "system_state": "/tmp/emergency_snapshot_'$timestamp'_system.txt",
            "config_backup": "/tmp/emergency_snapshot_'$timestamp'_config/",
            "git_commit_file": "/tmp/emergency_snapshot_'$timestamp'_git.txt"
        }
    }'
    
    redis-cli hset "emergency:snapshots:$snapshot_id" metadata "$snapshot_metadata"
    
    success "Emergency snapshot created: $snapshot_id"
    info "Snapshot files saved to /tmp/emergency_snapshot_${timestamp}_*"
}

# Send emergency notifications
send_emergency_notification() {
    local severity=${1:-"critical"}
    local message=${2:-"Emergency condition detected"}
    local details=${3:-""}
    
    info "Sending emergency notification: $severity"
    
    # Slack notification
    local slack_webhook=$(yq eval '.emergency_contacts[] | select(.type == "slack").webhook_url' "$CONFIG_FILE")
    if [[ -n "$slack_webhook" && "$slack_webhook" != "null" ]]; then
        local slack_message="{
            \"text\": \"🚨 RobertAI Emergency Alert\",
            \"attachments\": [{
                \"color\": \"danger\",
                \"fields\": [
                    {\"title\": \"Severity\", \"value\": \"$severity\", \"short\": true},
                    {\"title\": \"Time\", \"value\": \"$(date)\", \"short\": true},
                    {\"title\": \"Message\", \"value\": \"$message\", \"short\": false},
                    {\"title\": \"Details\", \"value\": \"$details\", \"short\": false}
                ]
            }]
        }"
        
        curl -X POST -H 'Content-type: application/json' \
            --data "$slack_message" \
            "$slack_webhook" &> /dev/null || warn "Failed to send Slack notification"
    fi
    
    # Email notification (using system mail if available)
    local email_address=$(yq eval '.emergency_contacts[] | select(.type == "email").address' "$CONFIG_FILE")
    if [[ -n "$email_address" && "$email_address" != "null" ]] && command -v mail &> /dev/null; then
        {
            echo "RobertAI Emergency Alert"
            echo
            echo "Severity: $severity"
            echo "Timestamp: $(date -Iseconds)"
            echo "Message: $message"
            echo "Details: $details"
            echo
            echo "System Status:"
            get_system_status
        } | mail -s "[RobertAI EMERGENCY] $severity - $message" "$email_address" || warn "Failed to send email notification"
    fi
    
    success "Emergency notification sent"
}

# System health check
health_check() {
    info "Running comprehensive health check..."
    
    local health_status=0
    local issues=()
    
    # Service health checks
    local services=("robertai-load-balancer" "robertai-queue-processor" "robertai-cache" "robertai-monitoring")
    for service in "${services[@]}"; do
        if ! systemctl is-active --quiet "$service"; then
            issues+=("Service $service is not running")
            health_status=1
        fi
    done
    
    # Load balancer health check
    local lb_response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health || echo "000")
    if [[ "$lb_response" != "200" ]]; then
        issues+=("Load balancer health check failed (HTTP $lb_response)")
        health_status=1
    fi
    
    # Database connectivity
    if ! redis-cli ping &> /dev/null; then
        issues+=("Redis connection failed")
        health_status=1
    fi
    
    # Queue health check
    local queue_depth=$(redis-cli llen "messages:high_priority" 2>/dev/null || echo "unknown")
    if [[ "$queue_depth" == "unknown" ]]; then
        issues+=("Cannot check queue status")
        health_status=1
    elif [[ "$queue_depth" -gt 1000 ]]; then
        issues+=("High priority queue depth is high: $queue_depth")
        health_status=1
    fi
    
    # AWS infrastructure check
    local asg_name=$(yq eval '.aws.auto_scaling_group' "$CONFIG_FILE")
    if [[ -n "$asg_name" && "$asg_name" != "null" ]]; then
        local unhealthy_instances=$(aws autoscaling describe-auto-scaling-groups \
            --auto-scaling-group-names "$asg_name" \
            --query 'AutoScalingGroups[0].Instances[?HealthStatus!=`Healthy`]' \
            --output json | jq length)
        
        if [[ "$unhealthy_instances" -gt 0 ]]; then
            issues+=("$unhealthy_instances unhealthy instances in Auto Scaling Group")
            health_status=1
        fi
    fi
    
    # Report results
    if [[ $health_status -eq 0 ]]; then
        success "All health checks passed"
        return 0
    else
        error "Health check failed with ${#issues[@]} issues:"
        for issue in "${issues[@]}"; do
            error "  - $issue"
        done
        return 1
    fi
}

# Rollback system to previous state
rollback_system() {
    local snapshot_id=${1:-""}
    
    if [[ -z "$snapshot_id" ]]; then
        error "Snapshot ID required for rollback"
        echo "Available snapshots:"
        redis-cli keys "emergency:snapshots:*" | sed 's/emergency:snapshots://g'
        return 1
    fi
    
    info "Rolling back system to snapshot: $snapshot_id"
    
    # Verify snapshot exists
    if ! redis-cli exists "emergency:snapshots:$snapshot_id" &> /dev/null; then
        error "Snapshot not found: $snapshot_id"
        return 1
    fi
    
    # Create backup before rollback
    create_emergency_snapshot "before_rollback_to_$snapshot_id"
    
    # Get snapshot metadata
    local snapshot_data=$(redis-cli hget "emergency:snapshots:$snapshot_id" metadata)
    local git_commit=$(echo "$snapshot_data" | jq -r '.git_commit')
    
    info "Rolling back to Git commit: $git_commit"
    
    # Stop services
    info "Stopping services for rollback..."
    local services=("robertai-monitoring" "robertai-queue-processor" "robertai-load-balancer" "robertai-cache")
    for service in "${services[@]}"; do
        systemctl stop "$service" || warn "Failed to stop $service"
    done
    
    # Git rollback
    if [[ -n "$git_commit" && "$git_commit" != "null" ]]; then
        git checkout "$git_commit" || error "Failed to checkout commit $git_commit"
    fi
    
    # Restore configuration
    local config_backup_path="/tmp/emergency_snapshot_${snapshot_id#emergency_}_config/"
    if [[ -d "$config_backup_path" ]]; then
        cp -r "$config_backup_path"* "${PROJECT_ROOT}/config/"
    fi
    
    # Restart services
    info "Starting services after rollback..."
    for service in "${services[@]}"; do
        systemctl start "$service" || error "Failed to start $service"
        sleep 5
    done
    
    # Validate rollback
    info "Validating rollback..."
    sleep 30
    if health_check; then
        success "System rollback completed successfully"
        send_emergency_notification "info" "System rollback completed" "Rolled back to snapshot: $snapshot_id"
    else
        error "System rollback validation failed"
        send_emergency_notification "critical" "System rollback failed" "Failed rollback to snapshot: $snapshot_id"
    fi
}

# Monitor system continuously
monitor_system() {
    info "Starting continuous system monitoring..."
    
    # Write PID file
    echo $$ > "$PIDFILE"
    
    # Trap signals for graceful shutdown
    trap 'info "Stopping system monitor..."; rm -f "$PIDFILE"; exit 0' SIGTERM SIGINT
    
    local check_interval=30
    local failure_count=0
    local max_failures=3
    
    while true; do
        if health_check &> /dev/null; then
            failure_count=0
            info "System healthy - $(date)"
        else
            failure_count=$((failure_count + 1))
            warn "Health check failed ($failure_count/$max_failures) - $(date)"
            
            if [[ $failure_count -ge $max_failures ]]; then
                error "Maximum health check failures reached - triggering emergency response"
                emergency_response
                failure_count=0  # Reset counter after response
            fi
        fi
        
        sleep $check_interval
    done
}

# Full emergency response
emergency_response() {
    info "=== INITIATING FULL EMERGENCY RESPONSE ==="
    
    # Create emergency snapshot first
    create_emergency_snapshot "full_emergency_response"
    
    # Send immediate notification
    send_emergency_notification "emergency" "Full emergency response initiated" "System health check failures exceeded threshold"
    
    # Try to restart failed services first
    restart_failed_services
    
    # Wait and check if that helped
    sleep 30
    if health_check &> /dev/null; then
        success "Emergency response: Service restart resolved issues"
        return 0
    fi
    
    # Enable graceful degradation
    enable_graceful_degradation
    
    # Activate backup systems
    activate_backup_systems
    
    # Emergency scale up
    emergency_scale_up 25
    
    # Wait for stabilization
    info "Waiting for system stabilization..."
    sleep 120
    
    # Final health check
    if health_check &> /dev/null; then
        success "Emergency response completed successfully"
        send_emergency_notification "warning" "Emergency response completed" "System has been stabilized with degraded performance"
    else
        error "Emergency response failed to resolve issues"
        send_emergency_notification "emergency" "Emergency response failed" "Manual intervention required immediately"
    fi
}

# Main function
main() {
    local command=${1:-"help"}
    
    case "$command" in
        "status")
            get_system_status
            ;;
        "health")
            health_check
            ;;
        "monitor")
            monitor_system
            ;;
        "emergency")
            emergency_response
            ;;
        "scale-up")
            emergency_scale_up "${2:-20}"
            ;;
        "restart-services")
            restart_failed_services
            ;;
        "activate-backup")
            activate_backup_systems
            ;;
        "degradation")
            enable_graceful_degradation
            ;;
        "snapshot")
            create_emergency_snapshot "${2:-manual_snapshot}"
            ;;
        "rollback")
            rollback_system "${2:-}"
            ;;
        "notify")
            send_emergency_notification "${2:-critical}" "${3:-Emergency test}" "${4:-Test notification}"
            ;;
        "help"|*)
            echo "RobertAI Emergency Procedures Script"
            echo
            echo "Usage: $0 <command> [args...]"
            echo
            echo "Commands:"
            echo "  status              - Show current system status"
            echo "  health              - Run comprehensive health check"
            echo "  monitor             - Start continuous monitoring (daemon mode)"
            echo "  emergency           - Execute full emergency response"
            echo "  scale-up [N]        - Emergency scale up to N instances (default: 20)"
            echo "  restart-services    - Restart all failed services"
            echo "  activate-backup     - Activate backup systems"
            echo "  degradation         - Enable graceful degradation mode"
            echo "  snapshot [reason]   - Create emergency snapshot"
            echo "  rollback <id>       - Rollback to snapshot ID"
            echo "  notify <sev> <msg>  - Send test notification"
            echo "  help                - Show this help"
            echo
            echo "Examples:"
            echo "  $0 status"
            echo "  $0 emergency"
            echo "  $0 scale-up 30"
            echo "  $0 rollback emergency_20240304_142030"
            ;;
    esac
}

# Validate environment before running any command
validate_environment

# Run main function with all arguments
main "$@"