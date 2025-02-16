import os
import sys
import json
import shutil
import subprocess
import re
from git import Repo, GitCommandError
from pathlib import Path
import yaml
import ast

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
                    pkg = line.split('==')[0] if '==' in line else re.split('[<>=]', line)[0]
                    dependencies[pkg.lower()] = "specified in requirements.txt"
    if pipfile.exists():
        dependencies['pipfile'] = "present"
    if setup_py.exists():
        dependencies['setup.py'] = "present"
    return dependencies

def extract_java_dependencies(repo_path):
    pom_xml = repo_path / 'pom.xml'
    dependencies = {}
    if pom_xml.exists():
        dependencies['pom.xml'] = "present"
    return dependencies

def extract_ruby_dependencies(repo_path):
    gemfile = repo_path / 'Gemfile'
    dependencies = {}
    if gemfile.exists():
        dependencies['gemfile'] = "present"
    return dependencies

def extract_dependencies(project_type, repo_path):
    dependencies = {}
    dev_dependencies = {}
    scripts = {}
    if project_type == 'Node.js':
        deps, dev_deps, scr = extract_node_dependencies(repo_path)
        dependencies = {k.lower(): v for k, v in deps.items()}
        dev_dependencies = {k.lower(): v for k, v in dev_deps.items()}
        scripts = scr
    elif project_type == 'Python':
        deps = extract_python_dependencies(repo_path)
        dependencies = {k.lower(): v for k, v in deps.items()}
    elif project_type == 'Java':
        deps = extract_java_dependencies(repo_path)
        dependencies = {k.lower(): v for k, v in deps.items()}
    elif project_type == 'Ruby':
        deps = extract_ruby_dependencies(repo_path)
        dependencies = {k.lower(): v for k, v in deps.items()}
    else:
        dependencies = {"info": "Unknown project type or no standard dependency files found."}
    return dependencies, dev_dependencies, scripts

def detect_frameworks(project_type, dependencies):
    frameworks = []
    if project_type == 'Node.js':
        if 'react' in dependencies or 'react' in dependencies:
            frameworks.append('React')
        if 'vue' in dependencies or 'vue.js' in dependencies:
            frameworks.append('Vue.js')
        if 'angular' in dependencies or 'angular.js' in dependencies:
            frameworks.append('Angular')
    elif project_type == 'Python':
        if 'fastapi' in dependencies or 'fastapi' in dependencies:
            frameworks.append('FastAPI')
        if 'django' in dependencies or 'django' in dependencies:
            frameworks.append('Django')
        if 'flask' in dependencies or 'flask' in dependencies:
            frameworks.append('Flask')
    elif project_type == 'Java':
        if 'spring-boot' in dependencies.get('pom.xml', '').lower():
            frameworks.append('Spring Boot')
    elif project_type == 'Ruby':
        if 'rails' in dependencies.get('gemfile', '').lower():
            frameworks.append('Ruby on Rails')
    return frameworks

def parse_dockerfile(repo_path):
    dockerfile = repo_path / 'Dockerfile'
    docker_info = {}
    if dockerfile.exists():
        with open(dockerfile, 'r') as f:
            content = f.read()
            # Extract FROM line
            from_match = re.search(r'^FROM\s+([^\s]+)', content, re.MULTILINE)
            if from_match:
                docker_info['Base Image'] = from_match.group(1)
            # Extract EXPOSE ports
            expose_matches = re.findall(r'^EXPOSE\s+(\d+)', content, re.MULTILINE)
            if expose_matches:
                docker_info['Exposed Ports'] = expose_matches
            # Extract ENV variables
            env_matches = re.findall(r'^ENV\s+([A-Z0-9_]+)=(.+)', content, re.MULTILINE)
            if env_matches:
                env_vars = {k: v for k, v in env_matches}
                docker_info['Environment Variables'] = env_vars
            # Extract VOLUME
            volume_matches = re.findall(r'^VOLUME\s+\[?"?([^\]"]+)"?\]', content, re.MULTILINE)
            if volume_matches:
                docker_info['Volumes'] = volume_matches
    return docker_info

def parse_docker_compose(repo_path):
    docker_compose = repo_path / 'docker-compose.yml'
    compose_info = {}
    if docker_compose.exists():
        with open(docker_compose, 'r') as f:
            try:
                data = yaml.safe_load(f)
                services = data.get('services', {})
                compose_info['Services'] = {}
                for service_name, service_data in services.items():
                    service_details = {}
                    image = service_data.get('image')
                    if image:
                        service_details['Image'] = image
                    build = service_data.get('build')
                    if build:
                        service_details['Build'] = build
                    ports = service_data.get('ports')
                    if ports:
                        service_details['Ports'] = ports
                    environment = service_data.get('environment')
                    if environment:
                        service_details['Environment Variables'] = environment
                    volumes = service_data.get('volumes')
                    if volumes:
                        service_details['Volumes'] = volumes
                    depends_on = service_data.get('depends_on')
                    if depends_on:
                        service_details['Depends On'] = depends_on
                    networks = service_data.get('networks')
                    if networks:
                        service_details['Networks'] = networks
                    compose_info['Services'][service_name] = service_details
                # External dependencies like networks and volumes
                networks = data.get('networks')
                if networks:
                    compose_info['Networks'] = networks
                volumes = data.get('volumes')
                if volumes:
                    compose_info['Volumes'] = volumes
            except yaml.YAMLError as exc:
                print(f"Error parsing docker-compose.yml: {exc}")
    return compose_info

def parse_kubernetes_manifests(repo_path):
    kubernetes_info = {}
    # Look for manifests in 'kubernetes/' directory or any '*.yaml' files
    possible_dirs = ['kubernetes', 'deployments', 'manifests']
    yaml_files = []
    for dir_name in possible_dirs:
        dir_path = repo_path / dir_name
        if dir_path.exists() and dir_path.is_dir():
            yaml_files.extend(dir_path.rglob('*.yaml'))
    # Additionally, include any YAML files in the root directory
    yaml_files.extend(repo_path.rglob('*.yaml'))
    # Filter out docker-compose.yml if present
    yaml_files = [f for f in yaml_files if f.name != 'docker-compose.yml']
    for yaml_file in yaml_files:
        with open(yaml_file, 'r') as f:
            try:
                data = yaml.safe_load_all(f)
                for doc in data:
                    if not doc:
                        continue
                    kind = doc.get('kind')
                    metadata = doc.get('metadata', {})
                    name = metadata.get('name')
                    if kind and name:
                        if kind not in kubernetes_info:
                            kubernetes_info[kind] = {}
                        kubernetes_info[kind][name] = doc
            except yaml.YAMLError as exc:
                print(f"Error parsing {yaml_file}: {exc}")
    return kubernetes_info

def detect_external_dependencies(docker_compose_info, kubernetes_info):
    external_deps = []
    # From Docker Compose Services
    if 'Services' in docker_compose_info:
        for service, details in docker_compose_info['Services'].items():
            image = details.get('Image')
            if image:
                # Identify services based on common images
                if 'mysql' in image.lower() or 'postgres' in image.lower() or 'mongodb' in image.lower():
                    external_deps.append({'Service': service, 'Type': 'Database', 'Image': image})
                elif 'redis' in image.lower():
                    external_deps.append({'Service': service, 'Type': 'Cache', 'Image': image})
                elif 'kafka' in image.lower() or 'zookeeper' in image.lower():
                    external_deps.append({'Service': service, 'Type': 'Message Broker', 'Image': image})
                elif 'elasticsearch' in image.lower():
                    external_deps.append({'Service': service, 'Type': 'Search Engine', 'Image': image})
                elif 'prometheus' in image.lower() or 'grafana' in image.lower():
                    external_deps.append({'Service': service, 'Type': 'Monitoring', 'Image': image})
                elif 'ollama' in image.lower() or 'vllm' in image.lower() or 'weaviate' in image.lower():
                    external_deps.append({'Service': service, 'Type': 'AI/ML Framework', 'Image': image})
    # From Kubernetes Manifests
    for kind, items in kubernetes_info.items():
        for name, details in items.items():
            if kind == 'Deployment':
                containers = details.get('spec', {}).get('template', {}).get('spec', {}).get('containers', [])
                for container in containers:
                    image = container.get('image', '')
                    if 'mysql' in image.lower() or 'postgres' in image.lower() or 'mongodb' in image.lower():
                        external_deps.append({'Service': name, 'Type': 'Database', 'Image': image})
                    elif 'redis' in image.lower():
                        external_deps.append({'Service': name, 'Type': 'Cache', 'Image': image})
                    elif 'kafka' in image.lower() or 'zookeeper' in image.lower():
                        external_deps.append({'Service': name, 'Type': 'Message Broker', 'Image': image})
                    elif 'elasticsearch' in image.lower():
                        external_deps.append({'Service': name, 'Type': 'Search Engine', 'Image': image})
                    elif 'prometheus' in image.lower() or 'grafana' in image.lower():
                        external_deps.append({'Service': name, 'Type': 'Monitoring', 'Image': image})
                    elif 'ollama' in image.lower() or 'vllm' in image.lower() or 'weaviate' in image.lower():
                        external_deps.append({'Service': name, 'Type': 'AI/ML Framework', 'Image': image})
    # Remove duplicates
    unique_deps = [dict(t) for t in {tuple(d.items()) for d in external_deps}]
    return unique_deps

def scan_python_imports(repo_path):
    dependencies_found = set()
    for file_path in repo_path.rglob('*.py'):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                node = ast.parse(f.read(), filename=str(file_path))
                for stmt in ast.walk(node):
                    if isinstance(stmt, ast.Import):
                        for alias in stmt.names:
                            dependencies_found.add(alias.name.split('.')[0].lower())
                    elif isinstance(stmt, ast.ImportFrom):
                        if stmt.module:
                            dependencies_found.add(stmt.module.split('.')[0].lower())
        except (SyntaxError, UnicodeDecodeError) as e:
            print(f"Error parsing {file_path}: {e}")
    return dependencies_found

def scan_nodejs_imports(repo_path):
    # Patterns for import and require statements
    import_re = re.compile(r'import\s+(?:.+?\s+from\s+)?[\'"]([^\'"]+)[\'"]', re.MULTILINE)
    require_re = re.compile(r'require\([\'"]([^\'"]+)[\'"]\)', re.MULTILINE)
    dependencies_found = set()
    for file_path in repo_path.rglob('*.{js,jsx,ts,tsx}'):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                imports = import_re.findall(content)
                requires = require_re.findall(content)
                for module in imports + requires:
                    # Exclude relative imports
                    if not module.startswith('.'):
                        # Extract the top-level package name
                        package = module.split('/')[0]
                        dependencies_found.add(package.lower())
        except (UnicodeDecodeError, IOError) as e:
            print(f"Error reading {file_path}: {e}")
    return dependencies_found

def generate_missing_dependencies(project_type, dependencies, code_dependencies):
    missing = {}
    if project_type == 'Python':
        declared = set(dependencies.keys())
        # Exclude standard library modules
        std_lib = {
            'base64', 'setuptools', 'typing', 'uuid', 'contextlib', 'logging',
            'fitz', 'json', 'os', 'io', 'collections', 're', 'enum'
        }
        missing_deps = (code_dependencies - declared) - std_lib
        missing = {dep: "used in source code but not declared in requirements.txt" for dep in missing_deps}
    elif project_type == 'Node.js':
        declared = set(dependencies.keys())
        missing_deps = code_dependencies - declared
        missing = {dep: "used in source code but not declared in package.json" for dep in missing_deps}
    return missing

def generate_report(repos_info, output_path):
    with open(output_path, 'w') as f:
        json.dump(repos_info, f, indent=4)
    print(f"Report generated at {output_path}")

def main():
    if len(sys.argv) < 3:
        print("Usage: python introspect_repos_deep.py <frontend_repo_url> <backend_repo_url>")
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
    frontend_dockerfile = parse_dockerfile(frontend_clone_dir)
    frontend_docker_compose = parse_docker_compose(frontend_clone_dir)
    frontend_kubernetes = parse_kubernetes_manifests(frontend_clone_dir)
    frontend_external_deps = detect_external_dependencies(frontend_docker_compose, frontend_kubernetes)
    
    # Scan frontend source code for additional dependencies
    frontend_code_dependencies = scan_nodejs_imports(frontend_clone_dir)
    frontend_missing_deps = generate_missing_dependencies(frontend_project_type, frontend_dependencies, frontend_code_dependencies)
    
    # Merge missing dependencies into Dependencies
    if frontend_missing_deps:
        frontend_dependencies.update(frontend_missing_deps)
    
    repos_info['dissertation-frontend'] = {
        'Repository URL': frontend_repo_url,
        'Project Type': frontend_project_type,
        'Frameworks': frontend_frameworks,
        'Dependencies': frontend_dependencies,
        'Dev Dependencies': frontend_dev_dependencies,
        'Scripts': frontend_scripts,
        'Dockerfile': frontend_dockerfile,
        'Docker Compose': frontend_docker_compose,
        'Kubernetes Manifests': frontend_kubernetes,
        'External Dependencies': frontend_external_deps
    }
    
    # Analyze Backend Repository
    backend_project_type = identify_project_type(backend_clone_dir)
    backend_dependencies, backend_dev_dependencies, backend_scripts = extract_dependencies(backend_project_type, backend_clone_dir)
    backend_frameworks = detect_frameworks(backend_project_type, backend_dependencies)
    backend_dockerfile = parse_dockerfile(backend_clone_dir)
    backend_docker_compose = parse_docker_compose(backend_clone_dir)
    backend_kubernetes = parse_kubernetes_manifests(backend_clone_dir)
    backend_external_deps = detect_external_dependencies(backend_docker_compose, backend_kubernetes)
    
    # Scan backend source code for additional dependencies
    backend_code_dependencies = scan_python_imports(backend_clone_dir)
    backend_missing_deps = generate_missing_dependencies(backend_project_type, backend_dependencies, backend_code_dependencies)
    
    # Merge missing dependencies into Dependencies
    if backend_missing_deps:
        backend_dependencies.update(backend_missing_deps)
    
    repos_info['Dissertation-Analysis'] = {
        'Repository URL': backend_repo_url,
        'Project Type': backend_project_type,
        'Frameworks': backend_frameworks,
        'Dependencies': backend_dependencies,
        'Dev Dependencies': backend_dev_dependencies,
        'Scripts': backend_scripts,
        'Dockerfile': backend_dockerfile,
        'Docker Compose': backend_docker_compose,
        'Kubernetes Manifests': backend_kubernetes,
        'External Dependencies': backend_external_deps
    }
    
    # Clean up cloned repositories
    shutil.rmtree(temp_dir)
    
    # Generate Report
    output_report = 'migration_report_deep_comprehensive.json'
    generate_report(repos_info, output_report)
    
    # Print the report in a readable format
    print("\n=== Migration Report ===")
    print(json.dumps(repos_info, indent=4))
    print("\nPlease refer to migration_report_deep_comprehensive.json for detailed information.")

if __name__ == "__main__":
    main()

