#!/usr/bin/env python3
"""
Claude Code Configuration Validator for RobertAI Bird.com AI Employee
Validates agent definitions, tool configurations, and system setup
Enhanced with namespace validation and BMad-core compatibility checks
"""

import json
import os
import sys
import re
from pathlib import Path

# Simple YAML parser for basic configs (avoiding external dependency)
def simple_yaml_load(file_path):
    """Simple YAML loader for basic key-value configs"""
    config = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    config[key] = value
    except Exception as e:
        print(f"Error loading YAML: {e}")
    return config

def validate_directory_structure():
    """Validate .claude directory structure"""
    # When run from .claude directory, adjust paths
    current_dir = os.getcwd()
    if current_dir.endswith('.claude'):
        required_dirs = ['.', 'agents', 'tools']
    else:
        required_dirs = ['.claude', '.claude/agents', '.claude/tools']
    missing_dirs = []
    
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
    
    return {
        "status": "passed" if not missing_dirs else "failed",
        "missing_directories": missing_dirs,
        "found_directories": [d for d in required_dirs if d not in missing_dirs]
    }

def validate_settings_file():
    """Validate settings.local.json configuration"""
    current_dir = os.getcwd()
    if current_dir.endswith('.claude'):
        settings_path = 'settings.local.json'
    else:
        settings_path = '.claude/settings.local.json'
    
    if not os.path.exists(settings_path):
        return {
            "status": "failed",
            "error": "settings.local.json not found"
        }
    
    try:
        with open(settings_path, 'r') as f:
            settings = json.load(f)
        
        # Check required structure
        required_keys = ['permissions']
        missing_keys = [key for key in required_keys if key not in settings]
        
        # Check permissions structure
        permissions_valid = True
        permissions_issues = []
        
        if 'permissions' in settings:
            perm = settings['permissions']
            if 'allow' not in perm:
                permissions_issues.append("Missing 'allow' array in permissions")
                permissions_valid = False
            elif not isinstance(perm['allow'], list):
                permissions_issues.append("'allow' must be an array")
                permissions_valid = False
        
        return {
            "status": "passed" if not missing_keys and permissions_valid else "failed",
            "missing_keys": missing_keys,
            "permissions_issues": permissions_issues,
            "allowed_permissions": len(settings.get('permissions', {}).get('allow', []))
        }
        
    except json.JSONDecodeError as e:
        return {
            "status": "failed",
            "error": f"Invalid JSON in settings.local.json: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "failed",
            "error": f"Error reading settings.local.json: {str(e)}"
        }

def validate_tools_json():
    """Validate tools.json configuration"""
    current_dir = os.getcwd()
    if current_dir.endswith('.claude'):
        tools_path = 'tools.json'
    else:
        tools_path = '.claude/tools.json'
    
    if not os.path.exists(tools_path):
        return {
            "status": "failed",
            "error": "tools.json not found"
        }
    
    try:
        with open(tools_path, 'r') as f:
            tools = json.load(f)
        
        expected_tools = [
            'analyze_multimodal',
            'bird_api_client', 
            'conversation_flow',
            'whatsapp_handler',
            'knowledge_base',
            'workflow_orchestrator'
        ]
        
        found_tools = list(tools.keys())
        missing_tools = [tool for tool in expected_tools if tool not in found_tools]
        extra_tools = [tool for tool in found_tools if tool not in expected_tools]
        
        # Validate tool structure
        tool_validation_issues = []
        for tool_name, tool_config in tools.items():
            required_fields = ['name', 'description', 'input_schema', 'command', 'args']
            missing_fields = [field for field in required_fields if field not in tool_config]
            if missing_fields:
                tool_validation_issues.append({
                    "tool": tool_name,
                    "missing_fields": missing_fields
                })
        
        return {
            "status": "passed" if not missing_tools and not tool_validation_issues else "failed",
            "expected_tools": len(expected_tools),
            "found_tools": len(found_tools),
            "missing_tools": missing_tools,
            "extra_tools": extra_tools,
            "validation_issues": tool_validation_issues
        }
        
    except json.JSONDecodeError as e:
        return {
            "status": "failed", 
            "error": f"Invalid JSON in tools.json: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "failed",
            "error": f"Error reading tools.json: {str(e)}"
        }

def validate_agents():
    """Validate agent configurations"""
    current_dir = os.getcwd()
    if current_dir.endswith('.claude'):
        agents_dir = 'agents'
    else:
        agents_dir = '.claude/agents'
    
    if not os.path.exists(agents_dir):
        return {
            "status": "failed",
            "error": "agents directory not found"
        }
    
    expected_agents = [
        'bird-master.md',
        'multimodal-analyst.md', 
        'conversation-designer.md',
        'integration-engineer.md',
        'whatsapp-specialist.md'
    ]
    
    found_agents = []
    agent_validation_issues = []
    
    for agent_file in expected_agents:
        agent_path = os.path.join(agents_dir, agent_file)
        if os.path.exists(agent_path):
            found_agents.append(agent_file)
            
            # Validate agent file structure
            try:
                with open(agent_path, 'r') as f:
                    content = f.read()
                
                # Check for frontmatter
                if not content.startswith('---'):
                    agent_validation_issues.append({
                        "agent": agent_file,
                        "issue": "Missing frontmatter"
                    })
                
                # Check for required sections
                required_sections = ['<identity>', '<responsibilities>', '<commands>', '<principles>']
                missing_sections = [section for section in required_sections if section not in content]
                if missing_sections:
                    agent_validation_issues.append({
                        "agent": agent_file,
                        "issue": f"Missing sections: {', '.join(missing_sections)}"
                    })
                    
            except Exception as e:
                agent_validation_issues.append({
                    "agent": agent_file,
                    "issue": f"Error reading file: {str(e)}"
                })
    
    missing_agents = [agent for agent in expected_agents if agent not in found_agents]
    
    return {
        "status": "passed" if not missing_agents and not agent_validation_issues else "failed",
        "expected_agents": len(expected_agents),
        "found_agents": len(found_agents),
        "missing_agents": missing_agents,
        "validation_issues": agent_validation_issues
    }

def validate_namespace_conventions():
    """Validate namespace conventions for compatibility with .bmad-core"""
    issues = []
    
    # Check tools.json for namespace conflicts
    current_dir = os.getcwd()
    if current_dir.endswith('.claude'):
        tools_path = 'tools.json'
    else:
        tools_path = '.claude/tools.json'
        
    if os.path.exists(tools_path):
        try:
            with open(tools_path, 'r') as f:
                tools = json.load(f)
            
            reserved_prefixes = ['bmad', 'BMad']
            for tool_name in tools.keys():
                for prefix in reserved_prefixes:
                    if tool_name.lower().startswith(prefix.lower()):
                        issues.append(f"Tool '{tool_name}' conflicts with reserved BMad namespace")
            
            # Check tool naming patterns
            valid_pattern = re.compile(r'^[a-z]+_[a-z_]+$')
            for tool_name in tools.keys():
                if not valid_pattern.match(tool_name):
                    issues.append(f"Tool '{tool_name}' doesn't follow naming convention (lowercase_with_underscores)")
                    
        except Exception as e:
            issues.append(f"Error validating tool names: {str(e)}")
    
    # Check agents directory for naming conflicts
    if current_dir.endswith('.claude'):
        agents_path = 'agents'
    else:
        agents_path = '.claude/agents'
        
    if os.path.exists(agents_path):
        agent_files = os.listdir(agents_path)
        for agent_file in agent_files:
            if agent_file.startswith('bmad') or agent_file.startswith('BMad'):
                issues.append(f"Agent '{agent_file}' conflicts with reserved BMad namespace")
    
    return {
        "status": "passed" if not issues else "failed",
        "issues": issues
    }

def validate_bmad_compatibility():
    """Check compatibility with .bmad-core configuration"""
    compatibility_issues = []
    
    # Check if .bmad-core exists and get its configuration
    if os.path.exists('.bmad-core/core-config.yaml'):
        try:
            bmad_config = simple_yaml_load('../.bmad-core/core-config.yaml')
            
            # Check for conflicting file paths
            bmad_paths = set()
            
            # Extract BMad paths
            if 'prd' in bmad_config:
                prd_config = bmad_config['prd']
                bmad_paths.add(prd_config.get('prdFile', ''))
                bmad_paths.add(prd_config.get('prdShardedLocation', ''))
            
            if 'architecture' in bmad_config:
                arch_config = bmad_config['architecture']
                bmad_paths.add(arch_config.get('architectureFile', ''))
                bmad_paths.add(arch_config.get('architectureShardedLocation', ''))
            
            # Check Claude tools for path conflicts
            if os.path.exists('.claude/tools.json'):
                with open('.claude/tools.json', 'r') as f:
                    claude_tools = json.load(f)
                
                for tool_name, tool_config in claude_tools.items():
                    if 'args' in tool_config:
                        for arg in tool_config['args']:
                            if isinstance(arg, str) and arg.startswith('.claude/tools/'):
                                for bmad_path in bmad_paths:
                                    if arg == bmad_path:
                                        compatibility_issues.append(f"Path conflict: {arg} used by both Claude and BMad")
            
        except Exception as e:
            compatibility_issues.append(f"Error checking BMad compatibility: {str(e)}")
    else:
        compatibility_issues.append("BMad core configuration not found - ensure .bmad-core/core-config.yaml exists")
    
    return {
        "status": "passed" if not compatibility_issues else "failed", 
        "issues": compatibility_issues
    }

def validate_python_tools():
    """Validate Python tool implementations"""
    tools_dir = '.claude/tools'
    
    expected_python_tools = [
        'analyze_multimodal.py',
        'bird_api_client.py',
        'conversation_flow.py', 
        'whatsapp_handler.py',
        'knowledge_base.py',
        'workflow_orchestrator.py'
    ]
    
    found_tools = []
    tool_issues = []
    
    for tool_file in expected_python_tools:
        tool_path = os.path.join(tools_dir, tool_file)
        if os.path.exists(tool_path):
            found_tools.append(tool_file)
            
            # Check if executable
            if not os.access(tool_path, os.X_OK):
                tool_issues.append({
                    "tool": tool_file,
                    "issue": "Not executable - run 'chmod +x' on this file"
                })
            
            # Check for Python shebang
            try:
                with open(tool_path, 'r') as f:
                    first_line = f.readline().strip()
                if not first_line.startswith('#!/usr/bin/env python3'):
                    tool_issues.append({
                        "tool": tool_file,
                        "issue": "Missing or incorrect Python shebang"
                    })
            except Exception as e:
                tool_issues.append({
                    "tool": tool_file,
                    "issue": f"Error reading file: {str(e)}"
                })
    
    missing_tools = [tool for tool in expected_python_tools if tool not in found_tools]
    
    return {
        "status": "passed" if not missing_tools and not tool_issues else "failed", 
        "expected_tools": len(expected_python_tools),
        "found_tools": len(found_tools),
        "missing_tools": missing_tools,
        "tool_issues": tool_issues
    }

def validate_readme():
    """Validate README.md documentation"""
    readme_path = '.claude/README.md'
    
    if not os.path.exists(readme_path):
        return {
            "status": "failed",
            "error": "README.md not found"
        }
    
    try:
        with open(readme_path, 'r') as f:
            content = f.read()
        
        required_sections = [
            'Configuration Complete',
            'Specialized Agents', 
            'Custom Tools Created',
            'Usage Examples',
            'Key Features & Benefits',
            'Technical Architecture'
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in content:
                missing_sections.append(section)
        
        return {
            "status": "passed" if not missing_sections else "warning",
            "content_length": len(content),
            "missing_sections": missing_sections
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": f"Error reading README.md: {str(e)}"
        }

def run_full_validation():
    """Run complete configuration validation"""
    print("🔍 Validating Claude Code Configuration for RobertAI Bird.com AI Employee...\n")
    
    validation_results = {
        "directory_structure": validate_directory_structure(),
        "settings_file": validate_settings_file(),
        "tools_json": validate_tools_json(),
        "agents": validate_agents(),
        "namespace_conventions": validate_namespace_conventions(),
        "bmad_compatibility": validate_bmad_compatibility(),
        "python_tools": validate_python_tools(),
        "readme": validate_readme()
    }
    
    # Summary
    total_tests = len(validation_results)
    passed_tests = sum(1 for result in validation_results.values() if result["status"] == "passed")
    warning_tests = sum(1 for result in validation_results.values() if result["status"] == "warning")
    failed_tests = sum(1 for result in validation_results.values() if result["status"] == "failed")
    
    print("=" * 60)
    print("VALIDATION RESULTS")
    print("=" * 60)
    
    for test_name, result in validation_results.items():
        status_icon = "✅" if result["status"] == "passed" else "⚠️" if result["status"] == "warning" else "❌"
        print(f"{status_icon} {test_name.replace('_', ' ').title()}: {result['status'].upper()}")
        
        if result["status"] == "failed" and "error" in result:
            print(f"   Error: {result['error']}")
        elif result["status"] == "failed":
            if "missing_directories" in result and result["missing_directories"]:
                print(f"   Missing directories: {', '.join(result['missing_directories'])}")
            if "missing_tools" in result and result["missing_tools"]:
                print(f"   Missing tools: {', '.join(result['missing_tools'])}")
            if "missing_agents" in result and result["missing_agents"]:
                print(f"   Missing agents: {', '.join(result['missing_agents'])}")
            if "validation_issues" in result and result["validation_issues"]:
                for issue in result["validation_issues"]:
                    print(f"   Issue: {issue}")
            if "tool_issues" in result and result["tool_issues"]:
                for issue in result["tool_issues"]:
                    print(f"   {issue['tool']}: {issue['issue']}")
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"⚠️  Warnings: {warning_tests}")
    print(f"❌ Failed: {failed_tests}")
    
    if failed_tests == 0 and warning_tests == 0:
        print("\n🎉 All validations passed! Configuration is ready for use.")
        print("\nQuick Start:")
        print("  /bird-master")
        print("  *help")
    elif failed_tests == 0:
        print(f"\n⚠️  Configuration mostly ready with {warning_tests} warning(s).")
        print("Consider addressing warnings for optimal performance.")
    else:
        print(f"\n❌ Configuration has {failed_tests} issue(s) that need to be fixed.")
        print("Please address the failed validations above.")
    
    print("\n📚 Full documentation available in .claude/README.md")
    
    return validation_results

def main():
    """Main validation function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        # JSON output for programmatic use
        results = {
            "directory_structure": validate_directory_structure(),
            "settings_file": validate_settings_file(),
            "tools_json": validate_tools_json(),
            "agents": validate_agents(),
            "python_tools": validate_python_tools(),
            "readme": validate_readme()
        }
        print(json.dumps(results, indent=2))
    else:
        # Human-readable output
        run_full_validation()

if __name__ == "__main__":
    main()