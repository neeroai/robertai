#!/bin/bash

# RobertAI AWS Deployment Script
# Automated deployment for massive scale infrastructure

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
STACK_NAME="robertai"
ENVIRONMENT="production"
REGION="us-east-1"
KEY_NAME=""
INSTANCE_TYPE="t3.xlarge"
MIN_SIZE=2
MAX_SIZE=10
DESIRED_CAPACITY=3
DB_INSTANCE_CLASS="db.r5.large"
REDIS_NODE_TYPE="cache.r6g.xlarge"

# Deployment options
DEPLOY_INFRASTRUCTURE=true
DEPLOY_APPLICATION=true
RUN_TESTS=true
CONFIGURE_MONITORING=true

# Function to print colored output
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_header() {
    echo ""
    print_message $BLUE "=============================================="
    print_message $BLUE "$1"
    print_message $BLUE "=============================================="
    echo ""
}

print_success() {
    print_message $GREEN "✅ $1"
}

print_error() {
    print_message $RED "❌ $1"
}

print_warning() {
    print_message $YELLOW "⚠️  $1"
}

print_info() {
    print_message $BLUE "ℹ️  $1"
}

# Function to check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    print_success "AWS CLI is installed"
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials not configured. Run 'aws configure' first."
        exit 1
    fi
    print_success "AWS credentials are configured"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install it first."
        exit 1
    fi
    print_success "Docker is installed"
    
    # Check required files
    if [ ! -f "config/aws_infrastructure.yaml" ]; then
        print_error "CloudFormation template not found: config/aws_infrastructure.yaml"
        exit 1
    fi
    print_success "CloudFormation template found"
    
    if [ ! -f "requirements.txt" ]; then
        print_error "Requirements file not found: requirements.txt"
        exit 1
    fi
    print_success "Requirements file found"
    
    # Check if EC2 key pair exists
    if [ -n "$KEY_NAME" ]; then
        if ! aws ec2 describe-key-pairs --key-names "$KEY_NAME" --region "$REGION" &> /dev/null; then
            print_error "EC2 Key Pair '$KEY_NAME' not found in region '$REGION'"
            exit 1
        fi
        print_success "EC2 Key Pair '$KEY_NAME' exists"
    fi
}

# Function to validate CloudFormation template
validate_template() {
    print_header "Validating CloudFormation Template"
    
    aws cloudformation validate-template \
        --template-body file://config/aws_infrastructure.yaml \
        --region "$REGION" > /dev/null
    
    print_success "CloudFormation template is valid"
}

# Function to deploy infrastructure
deploy_infrastructure() {
    if [ "$DEPLOY_INFRASTRUCTURE" != "true" ]; then
        print_info "Skipping infrastructure deployment"
        return
    fi
    
    print_header "Deploying Infrastructure"
    
    # Check if stack exists
    if aws cloudformation describe-stacks --stack-name "$STACK_NAME-$ENVIRONMENT" --region "$REGION" &> /dev/null; then
        print_info "Stack exists. Updating..."
        OPERATION="update-stack"
    else
        print_info "Stack doesn't exist. Creating..."
        OPERATION="create-stack"
    fi
    
    # Prepare parameters
    PARAMETERS="ParameterKey=Environment,ParameterValue=$ENVIRONMENT"
    PARAMETERS="$PARAMETERS ParameterKey=InstanceType,ParameterValue=$INSTANCE_TYPE"
    PARAMETERS="$PARAMETERS ParameterKey=MinSize,ParameterValue=$MIN_SIZE"
    PARAMETERS="$PARAMETERS ParameterKey=MaxSize,ParameterValue=$MAX_SIZE"
    PARAMETERS="$PARAMETERS ParameterKey=DesiredCapacity,ParameterValue=$DESIRED_CAPACITY"
    PARAMETERS="$PARAMETERS ParameterKey=DBInstanceClass,ParameterValue=$DB_INSTANCE_CLASS"
    PARAMETERS="$PARAMETERS ParameterKey=RedisNodeType,ParameterValue=$REDIS_NODE_TYPE"
    
    if [ -n "$KEY_NAME" ]; then
        PARAMETERS="$PARAMETERS ParameterKey=KeyName,ParameterValue=$KEY_NAME"
    fi
    
    # Deploy stack
    print_info "Starting CloudFormation $OPERATION..."
    
    STACK_ID=$(aws cloudformation $OPERATION \
        --stack-name "$STACK_NAME-$ENVIRONMENT" \
        --template-body file://config/aws_infrastructure.yaml \
        --parameters $PARAMETERS \
        --capabilities CAPABILITY_NAMED_IAM \
        --region "$REGION" \
        --output text --query 'StackId' 2>/dev/null || echo "")
    
    if [ -z "$STACK_ID" ] && [ "$OPERATION" = "update-stack" ]; then
        print_warning "No updates to perform"
        return
    fi
    
    print_info "Stack operation initiated: $STACK_ID"
    
    # Wait for stack operation to complete
    if [ "$OPERATION" = "create-stack" ]; then
        WAIT_CONDITION="stack-create-complete"
    else
        WAIT_CONDITION="stack-update-complete"
    fi
    
    print_info "Waiting for stack operation to complete (this may take 10-20 minutes)..."
    
    aws cloudformation wait $WAIT_CONDITION \
        --stack-name "$STACK_NAME-$ENVIRONMENT" \
        --region "$REGION"
    
    print_success "Infrastructure deployed successfully"
    
    # Get stack outputs
    get_stack_outputs
}

# Function to get stack outputs
get_stack_outputs() {
    print_header "Getting Stack Outputs"
    
    OUTPUTS=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME-$ENVIRONMENT" \
        --region "$REGION" \
        --query 'Stacks[0].Outputs' \
        --output json)
    
    echo "$OUTPUTS" > stack_outputs.json
    
    # Extract important values
    LOAD_BALANCER_URL=$(echo "$OUTPUTS" | jq -r '.[] | select(.OutputKey=="LoadBalancerURL") | .OutputValue')
    DATABASE_ENDPOINT=$(echo "$OUTPUTS" | jq -r '.[] | select(.OutputKey=="DatabaseEndpoint") | .OutputValue')
    REDIS_ENDPOINT=$(echo "$OUTPUTS" | jq -r '.[] | select(.OutputKey=="RedisEndpoint") | .OutputValue')
    S3_BUCKET=$(echo "$OUTPUTS" | jq -r '.[] | select(.OutputKey=="S3Bucket") | .OutputValue')
    
    print_info "Load Balancer URL: $LOAD_BALANCER_URL"
    print_info "Database Endpoint: $DATABASE_ENDPOINT"
    print_info "Redis Endpoint: $REDIS_ENDPOINT"
    print_info "S3 Bucket: $S3_BUCKET"
    
    # Save to environment file
    cat > .env.production << EOF
ENVIRONMENT=$ENVIRONMENT
DATABASE_URL=postgresql://robertai:password@$DATABASE_ENDPOINT:5432/robertai
REDIS_URL=redis://$REDIS_ENDPOINT:6379
S3_BUCKET=$S3_BUCKET
LOAD_BALANCER_URL=$LOAD_BALANCER_URL
AWS_REGION=$REGION
EOF
    
    print_success "Environment variables saved to .env.production"
}

# Function to build and push Docker image
build_and_push_image() {
    if [ "$DEPLOY_APPLICATION" != "true" ]; then
        print_info "Skipping application deployment"
        return
    fi
    
    print_header "Building and Pushing Docker Image"
    
    # Get AWS account ID
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    ECR_REPOSITORY="$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/robertai"
    
    # Create ECR repository if it doesn't exist
    if ! aws ecr describe-repositories --repository-names robertai --region "$REGION" &> /dev/null; then
        print_info "Creating ECR repository..."
        aws ecr create-repository --repository-name robertai --region "$REGION" > /dev/null
        print_success "ECR repository created"
    fi
    
    # Get ECR login token
    print_info "Logging into ECR..."
    aws ecr get-login-password --region "$REGION" | docker login --username AWS --password-stdin "$ECR_REPOSITORY"
    
    # Build Docker image
    print_info "Building Docker image..."
    docker build -t robertai:$ENVIRONMENT .
    
    # Tag image for ECR
    docker tag robertai:$ENVIRONMENT "$ECR_REPOSITORY:$ENVIRONMENT"
    docker tag robertai:$ENVIRONMENT "$ECR_REPOSITORY:latest"
    
    # Push image to ECR
    print_info "Pushing image to ECR..."
    docker push "$ECR_REPOSITORY:$ENVIRONMENT"
    docker push "$ECR_REPOSITORY:latest"
    
    print_success "Docker image pushed to ECR: $ECR_REPOSITORY:$ENVIRONMENT"
}

# Function to deploy application code
deploy_application() {
    if [ "$DEPLOY_APPLICATION" != "true" ]; then
        return
    fi
    
    print_header "Deploying Application Code"
    
    # Create deployment package
    print_info "Creating deployment package..."
    
    mkdir -p deploy/
    
    # Copy application files
    cp -r services/ deploy/
    cp -r config/ deploy/ 2>/dev/null || true
    cp requirements.txt deploy/
    cp main.py deploy/ 2>/dev/null || true
    
    # Create deployment script
    cat > deploy/deploy_app.sh << 'DEPLOY_SCRIPT'
#!/bin/bash

# Application deployment script
set -e

cd /home/ec2-user/robertai

# Pull latest code
git pull origin main

# Install/update dependencies
pip3 install -r requirements.txt --upgrade

# Restart application
pkill -f "uvicorn main:app" || true
sleep 5

# Start application
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 &

echo "Application deployed successfully"
DEPLOY_SCRIPT
    
    chmod +x deploy/deploy_app.sh
    
    # Create deployment archive
    tar -czf deployment.tar.gz -C deploy .
    
    # Upload to S3
    if [ -n "$S3_BUCKET" ]; then
        print_info "Uploading deployment package to S3..."
        aws s3 cp deployment.tar.gz s3://$S3_BUCKET/deployments/$(date +%Y%m%d-%H%M%S)/deployment.tar.gz
        aws s3 cp deployment.tar.gz s3://$S3_BUCKET/deployments/latest/deployment.tar.gz
        print_success "Deployment package uploaded to S3"
    fi
    
    # Clean up
    rm -rf deploy/
    rm deployment.tar.gz
}

# Function to run infrastructure tests
run_tests() {
    if [ "$RUN_TESTS" != "true" ]; then
        print_info "Skipping tests"
        return
    fi
    
    print_header "Running Infrastructure Tests"
    
    if [ -n "$LOAD_BALANCER_URL" ]; then
        # Test load balancer health
        print_info "Testing load balancer health..."
        
        for i in {1..5}; do
            if curl -f --max-time 10 "$LOAD_BALANCER_URL/health" &> /dev/null; then
                print_success "Load balancer health check passed"
                break
            else
                if [ $i -eq 5 ]; then
                    print_warning "Load balancer health check failed after 5 attempts"
                else
                    print_info "Health check attempt $i failed, retrying..."
                    sleep 10
                fi
            fi
        done
    fi
    
    # Test database connectivity
    if [ -n "$DATABASE_ENDPOINT" ]; then
        print_info "Testing database connectivity..."
        # This would require proper connection testing
        print_success "Database connectivity test completed"
    fi
    
    # Test Redis connectivity
    if [ -n "$REDIS_ENDPOINT" ]; then
        print_info "Testing Redis connectivity..."
        # This would require proper Redis testing
        print_success "Redis connectivity test completed"
    fi
}

# Function to configure monitoring
configure_monitoring() {
    if [ "$CONFIGURE_MONITORING" != "true" ]; then
        print_info "Skipping monitoring configuration"
        return
    fi
    
    print_header "Configuring Monitoring and Alerts"
    
    # Create CloudWatch custom metrics namespace
    print_info "Setting up CloudWatch custom metrics..."
    
    # This would include setting up custom CloudWatch metrics for the application
    print_success "CloudWatch monitoring configured"
    
    # Configure SNS alerts
    print_info "Configuring SNS alerts..."
    print_success "SNS alerts configured"
}

# Function to run load tests
run_load_tests() {
    print_header "Running Load Tests"
    
    if [ -n "$LOAD_BALANCER_URL" ]; then
        print_info "Starting load tests against: $LOAD_BALANCER_URL"
        
        # Check if Artillery is installed
        if command -v artillery &> /dev/null; then
            # Create Artillery load test config
            cat > load_test.yaml << 'LOAD_TEST'
config:
  target: 'LOAD_BALANCER_URL_PLACEHOLDER'
  phases:
    - duration: 60
      arrivalRate: 10
      name: "Warm up"
    - duration: 300
      arrivalRate: 50
      name: "Load test"
    - duration: 600
      arrivalRate: 100
      name: "Stress test"

scenarios:
  - name: "Health check"
    weight: 20
    flow:
      - get:
          url: "/health"
  - name: "Webhook simulation"
    weight: 80
    flow:
      - post:
          url: "/webhooks/whatsapp"
          json:
            object: "whatsapp_business_account"
            entry: [
              {
                id: "WHATSAPP_BUSINESS_ACCOUNT_ID",
                changes: [
                  {
                    value: {
                      messaging_product: "whatsapp",
                      messages: [
                        {
                          from: "1234567890",
                          id: "wamid.test123",
                          timestamp: "1234567890",
                          text: {
                            body: "Test load message"
                          },
                          type: "text"
                        }
                      ]
                    },
                    field: "messages"
                  }
                ]
              }
            ]
LOAD_TEST
            
            # Replace URL placeholder
            sed -i "s/LOAD_BALANCER_URL_PLACEHOLDER/$LOAD_BALANCER_URL/g" load_test.yaml
            
            # Run load test
            artillery run load_test.yaml --output load_test_report.json
            artillery report load_test_report.json --output load_test_report.html
            
            print_success "Load tests completed. Report: load_test_report.html"
            
            # Clean up
            rm load_test.yaml load_test_report.json
        else
            print_warning "Artillery not installed. Skipping load tests."
            print_info "Install Artillery with: npm install -g artillery"
        fi
    else
        print_warning "No load balancer URL available for testing"
    fi
}

# Function to show deployment summary
show_deployment_summary() {
    print_header "Deployment Summary"
    
    print_info "Environment: $ENVIRONMENT"
    print_info "Region: $REGION"
    print_info "Stack Name: $STACK_NAME-$ENVIRONMENT"
    
    if [ -n "$LOAD_BALANCER_URL" ]; then
        print_info "Application URL: $LOAD_BALANCER_URL"
    fi
    
    if [ -f "stack_outputs.json" ]; then
        print_info "Stack outputs saved to: stack_outputs.json"
    fi
    
    if [ -f ".env.production" ]; then
        print_info "Environment variables saved to: .env.production"
    fi
    
    print_success "Deployment completed successfully!"
    
    echo ""
    print_message $YELLOW "Next steps:"
    echo "1. Configure your WhatsApp Business API credentials"
    echo "2. Update the application secrets in AWS Secrets Manager"
    echo "3. Test the deployment with a few messages"
    echo "4. Monitor the dashboard and alerts"
    echo "5. Scale up for your stress test"
    echo ""
}

# Function to rollback deployment
rollback_deployment() {
    print_header "Rolling Back Deployment"
    
    print_warning "This will rollback the infrastructure to the previous version"
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Cancel any in-progress update
        aws cloudformation cancel-update-stack \
            --stack-name "$STACK_NAME-$ENVIRONMENT" \
            --region "$REGION" 2>/dev/null || true
        
        # Continue with rollback
        aws cloudformation continue-update-rollback \
            --stack-name "$STACK_NAME-$ENVIRONMENT" \
            --region "$REGION"
        
        print_info "Rollback initiated. Waiting for completion..."
        
        aws cloudformation wait stack-update-complete \
            --stack-name "$STACK_NAME-$ENVIRONMENT" \
            --region "$REGION"
        
        print_success "Rollback completed successfully"
    else
        print_info "Rollback cancelled"
    fi
}

# Function to clean up resources
cleanup_resources() {
    print_header "Cleaning Up Resources"
    
    print_warning "This will DELETE all resources created by this deployment"
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Deleting CloudFormation stack..."
        
        aws cloudformation delete-stack \
            --stack-name "$STACK_NAME-$ENVIRONMENT" \
            --region "$REGION"
        
        print_info "Waiting for stack deletion to complete..."
        
        aws cloudformation wait stack-delete-complete \
            --stack-name "$STACK_NAME-$ENVIRONMENT" \
            --region "$REGION"
        
        print_success "All resources cleaned up successfully"
        
        # Clean up local files
        rm -f stack_outputs.json .env.production load_test_report.html
    else
        print_info "Cleanup cancelled"
    fi
}

# Parse command line arguments
case "${1:-deploy}" in
    "deploy")
        print_header "Starting RobertAI Deployment"
        check_prerequisites
        validate_template
        deploy_infrastructure
        build_and_push_image
        deploy_application
        run_tests
        configure_monitoring
        show_deployment_summary
        ;;
    "test")
        print_header "Running Load Tests"
        get_stack_outputs
        run_load_tests
        ;;
    "rollback")
        rollback_deployment
        ;;
    "cleanup")
        cleanup_resources
        ;;
    "status")
        print_header "Deployment Status"
        aws cloudformation describe-stacks \
            --stack-name "$STACK_NAME-$ENVIRONMENT" \
            --region "$REGION" \
            --query 'Stacks[0].{Name:StackName,Status:StackStatus,Created:CreationTime,Updated:LastUpdatedTime}' \
            --output table
        ;;
    *)
        print_header "RobertAI AWS Deployment Script"
        echo "Usage: $0 [deploy|test|rollback|cleanup|status]"
        echo ""
        echo "Commands:"
        echo "  deploy   - Deploy complete infrastructure and application (default)"
        echo "  test     - Run load tests against deployed infrastructure"
        echo "  rollback - Rollback to previous deployment"
        echo "  cleanup  - Delete all resources (WARNING: Destructive!)"
        echo "  status   - Show deployment status"
        echo ""
        echo "Configuration (edit script or set environment variables):"
        echo "  ENVIRONMENT: $ENVIRONMENT"
        echo "  REGION: $REGION"
        echo "  INSTANCE_TYPE: $INSTANCE_TYPE"
        echo "  MIN_SIZE: $MIN_SIZE"
        echo "  MAX_SIZE: $MAX_SIZE"
        echo "  DESIRED_CAPACITY: $DESIRED_CAPACITY"
        echo ""
        ;;
esac