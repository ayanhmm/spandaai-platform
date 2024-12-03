import os
import sys
import json
import subprocess
import shutil
from git import Repo, GitCommandError
from pathlib import Path

def clone_repo(repo_url, clone_dir, branch='main'):
    try:
        print(f"Cloning {repo_url} into {clone_dir}...")
        Repo.clone_from(repo_url, clone_dir, branch=branch)
        print(f"Successfully cloned {repo_url}\n")
    except GitCommandError as e:
        print(f"Error cloning {repo_url}: {e}")
        sys.exit(1)

def identify_project_type(repo_path):
    if (repo_path / 'package.json').exists():
        return 'Node.js'
    elif (repo_path / 'requirements.txt').exists() or (repo_path / 'Pipfile').exists() or (repo_path / 'setup.py').exists():
        return 'Python'
    elif (repo_path / 'pom.xml').exists():
        return 'Java'
    elif (repo_path / 'Gemfile').exists():
        return 'Ruby'
    else:
        return 'Unknown'

def extract_node_dependencies(repo_path):
    package_json = repo_path / 'package.json'
    dependencies = {}
    dev_dependencies = {}
    scripts = {}
    if package_json.exists():
        with open(package_json, 'r') as f:
            data = json.load(f)
            dependencies = data.get('dependencies', {})
            dev_dependencies = data.get('devDependencies', {})
            scripts = data.get('scripts', {})
    return dependencies, dev_dependencies, scripts

def extract_python_dependencies(repo_path):
    requirements_txt = repo_path / 'requirements.txt'
    pipfile = repo_path / 'Pipfile'
    setup_py = repo_path / 'setup.py'
    dependencies = {}
    if requirements_txt.exists():
        with open(requirements_txt, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    pkg = line.split('==')[0] if '==' in line else line
                    dependencies[pkg] = "specified in requirements.txt"
    if pipfile.exists():
        # Parsing Pipfile can be more complex; here we just note its presence
        dependencies['Pipfile'] = "present"
    if setup_py.exists():
        # Parsing setup.py requires executing or parsing AST; here we note its presence
        dependencies['setup.py'] = "present"
    return dependencies

def extract_java_dependencies(repo_path):
    pom_xml = repo_path / 'pom.xml'
    dependencies = {}
    if pom_xml.exists():
        # Parsing pom.xml requires XML parsing; here we note its presence
        dependencies['pom.xml'] = "present"
    return dependencies

def extract_ruby_dependencies(repo_path):
    gemfile = repo_path / 'Gemfile'
    dependencies = {}
    if gemfile.exists():
        # Parsing Gemfile requires Ruby parsing; here we note its presence
        dependencies['Gemfile'] = "present"
    return dependencies

def extract_dependencies(project_type, repo_path):
    dependencies = {}
    dev_dependencies = {}
    scripts = {}
    if project_type == 'Node.js':
        deps, dev_deps, scr = extract_node_dependencies(repo_path)
        dependencies = deps
        dev_dependencies = dev_deps
        scripts = scr
    elif project_type == 'Python':
        deps = extract_python_dependencies(repo_path)
        dependencies = deps
    elif project_type == 'Java':
        deps = extract_java_dependencies(repo_path)
        dependencies = deps
    elif project_type == 'Ruby':
        deps = extract_ruby_dependencies(repo_path)
        dependencies = deps
    else:
        dependencies = {"Info": "Unknown project type or no standard dependency files found."}
    return dependencies, dev_dependencies, scripts

def detect_frameworks(project_type, dependencies):
    frameworks = []
    if project_type == 'Node.js':
        # Check for common frontend frameworks
        if 'react' in dependencies:
            frameworks.append('React')
        if 'vue' in dependencies:
            frameworks.append('Vue.js')
        if 'angular' in dependencies:
            frameworks.append('Angular')
    elif project_type == 'Python':
        # Check for Django, Flask, etc.
        if 'Django' in dependencies or 'django' in dependencies:
            frameworks.append('Django')
        if 'Flask' in dependencies or 'flask' in dependencies:
            frameworks.append('Flask')
    elif project_type == 'Java':
        # Check for Spring, etc.
        if 'spring-boot' in dependencies.get('pom.xml', '').lower():
            frameworks.append('Spring Boot')
    elif project_type == 'Ruby':
        # Check for Rails, etc.
        if 'rails' in dependencies.get('Gemfile', '').lower():
            frameworks.append('Ruby on Rails')
    return frameworks

def generate_report(repos_info, output_path):
    with open(output_path, 'w') as f:
        json.dump(repos_info, f, indent=4)
    print(f"Report generated at {output_path}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python introspect_repos.py <frontend_repo_url> <backend_repo_url>")
        sys.exit(1)
    
    frontend_repo_url = sys.argv[1]
    backend_repo_url = sys.argv[2]
    
    temp_dir = Path('temp_repos')
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Clone Frontend Repository
    frontend_clone_dir = temp_dir / 'dissertation-frontend'
    clone_repo(frontend_repo_url, frontend_clone_dir)
    
    # Clone Backend Repository
    backend_clone_dir = temp_dir / 'Dissertation-Analysis'
    clone_repo(backend_repo_url, backend_clone_dir)
    
    repos_info = {}
    
    # Analyze Frontend Repository
    frontend_project_type = identify_project_type(frontend_clone_dir)
    frontend_dependencies, frontend_dev_dependencies, frontend_scripts = extract_dependencies(frontend_project_type, frontend_clone_dir)
    frontend_frameworks = detect_frameworks(frontend_project_type, frontend_dependencies)
    
    repos_info['dissertation-frontend'] = {
        'Repository URL': frontend_repo_url,
        'Project Type': frontend_project_type,
        'Frameworks': frontend_frameworks,
        'Dependencies': frontend_dependencies,
        'Dev Dependencies': frontend_dev_dependencies,
        'Scripts': frontend_scripts
    }
    
    # Analyze Backend Repository
    backend_project_type = identify_project_type(backend_clone_dir)
    backend_dependencies, backend_dev_dependencies, backend_scripts = extract_dependencies(backend_project_type, backend_clone_dir)
    backend_frameworks = detect_frameworks(backend_project_type, backend_dependencies)
    
    repos_info['Dissertation-Analysis'] = {
        'Repository URL': backend_repo_url,
        'Project Type': backend_project_type,
        'Frameworks': backend_frameworks,
        'Dependencies': backend_dependencies,
        'Dev Dependencies': backend_dev_dependencies,
        'Scripts': backend_scripts
    }
    
    # Clean up cloned repositories
    shutil.rmtree(temp_dir)
    
    # Generate Report
    output_report = 'migration_report.json'
    generate_report(repos_info, output_report)
    
    # Print the report in a readable format
    print("\n=== Migration Report ===")
    print(json.dumps(repos_info, indent=4))
    print("\nPlease refer to migration_report.json for detailed information.")

if __name__ == "__main__":
    main()

