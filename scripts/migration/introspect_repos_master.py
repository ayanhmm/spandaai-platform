import os
import sys
import json
import shutil
import subprocess
import re
import time
from git import Repo, GitCommandError
from pathlib import Path
import yaml
import ast
import logging
import warnings
from ruamel.yaml import YAML
from logging.handlers import RotatingFileHandler

# Suppress SyntaxWarnings from cloned repositories
warnings.filterwarnings("ignore", category=SyntaxWarning)

# Configure logging with rotation to prevent log file from growing indefinitely
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create handlers
c_handler = logging.StreamHandler(sys.stdout)
f_handler = RotatingFileHandler("introspect_repos_master.log", maxBytes=5*1024*1024, backupCount=2)
c_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.INFO)

# Create formatters and add to handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
c_handler.setFormatter(formatter)
f_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)


def clone_repo(repo_url, clone_dir, auth_method=None, auth_token=None, retries=3, delay=5):
    """
    Clones a Git repository into the specified directory with a retry mechanism.
    Supports optional authentication via SSH or PAT.

    Parameters:
        repo_url (str): URL of the repository to clone.
        clone_dir (Path): Directory where the repository will be cloned.
        auth_method (str, optional): Authentication method ('ssh', 'pat', or None).
        auth_token (str, optional): Personal Access Token for PAT authentication.
        retries (int): Number of retry attempts.
        delay (int): Delay in seconds between retries.

    Returns:
        bool: True if cloning was successful, False otherwise.
    """
    attempt = 0
    while attempt < retries:
        try:
            logger.info(f"Cloning {repo_url} into {clone_dir} (Attempt {attempt + 1})...")

            # Modify repo_url for authentication if necessary
            if auth_method == 'ssh':
                # Ensure repo_url is in SSH format
                if repo_url.startswith('https://github.com/'):
                    repo_url = repo_url.replace('https://github.com/', 'git@github.com:')
                elif not repo_url.startswith('git@github.com:'):
                    logger.warning(f"Repository URL {repo_url} may not be in SSH format.")

            elif auth_method == 'pat' and auth_token:
                # Insert PAT into HTTPS URL
                if repo_url.startswith('https://'):
                    repo_url = repo_url.replace('https://', f'https://{auth_token}@')
                else:
                    logger.warning(f"PAT authentication is typically used with HTTPS URLs.")

            # Clone the repository without specifying the branch
            Repo.clone_from(repo_url, clone_dir)
            logger.info(f"Successfully cloned {repo_url}\n")
            return True
        except GitCommandError as e:
            logger.error(f"Error cloning {repo_url}: {e}")
            attempt += 1
            if attempt < retries:
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.error(f"Failed to clone {repo_url} after {retries} attempts.")
                return False


def identify_project_type(repo_path):
    """
    Identifies the project types based on specific files in the repository.

    Parameters:
        repo_path (Path): Path to the cloned repository.

    Returns:
        list: List of project types (e.g., ['Node.js', 'Python']).
    """
    project_types = []
    if (repo_path / 'package.json').exists():
        project_types.append('Node.js')
    if (repo_path / 'requirements.txt').exists() or (repo_path / 'Pipfile').exists() or (repo_path / 'setup.py').exists():
        project_types.append('Python')
    if (repo_path / 'pom.xml').exists() or (repo_path / 'build.gradle').exists():
        project_types.append('Java')
    if (repo_path / 'go.mod').exists():
        project_types.append('Go')
    if (repo_path / 'Gemfile').exists():
        project_types.append('Ruby')
    if (repo_path / 'Cargo.toml').exists():
        project_types.append('Rust')
    # Add more as needed

    if not project_types:
        project_types.append('Unknown')
    return project_types


def extract_node_dependencies(repo_path):
    """
    Extracts dependencies, devDependencies, and scripts from package.json.

    Parameters:
        repo_path (Path): Path to the Node.js repository.

    Returns:
        tuple: (dependencies dict, dev_dependencies dict, scripts dict)
    """
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
    """
    Extracts dependencies from requirements.txt, Pipfile, and setup.py.

    Parameters:
        repo_path (Path): Path to the Python repository.

    Returns:
        dict: Dependencies with their sources.
    """
    requirements_txt = repo_path / 'requirements.txt'
    pipfile = repo_path / 'Pipfile'
    setup_py = repo_path / 'setup.py'
    dependencies = {}
    if requirements_txt.exists():
        with open(requirements_txt, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Remove comments and inline specifications
                    line = line.split('#')[0].strip()
                    if not line:
                        continue
                    pkg = line.split('==')[0] if '==' in line else re.split('[<>=]', line)[0]
                    pkg = pkg.strip().lower()
                    if pkg:
                        dependencies[pkg] = "specified in requirements.txt"
    if pipfile.exists():
        dependencies['pipfile'] = "present in Pipfile"
    if setup_py.exists():
        dependencies['setup.py'] = "present in setup.py"
    return dependencies


def extract_java_dependencies(repo_path):
    """
    Extracts dependencies from pom.xml or build.gradle.

    Parameters:
        repo_path (Path): Path to the Java repository.

    Returns:
        dict: Dependencies with their sources.
    """
    pom_xml = repo_path / 'pom.xml'
    build_gradle = repo_path / 'build.gradle'
    dependencies = {}
    if pom_xml.exists():
        dependencies['pom.xml'] = "present in pom.xml"
    if build_gradle.exists():
        dependencies['build.gradle'] = "present in build.gradle"
    return dependencies


def extract_go_dependencies(repo_path):
    """
    Extracts dependencies from go.mod.

    Parameters:
        repo_path (Path): Path to the Go repository.

    Returns:
        dict: Dependencies with their sources.
    """
    go_mod = repo_path / 'go.mod'
    dependencies = {}
    if go_mod.exists():
        with open(go_mod, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('require'):
                    parts = line.split()
                    if len(parts) >= 3:
                        pkg = parts[1]
                        version = parts[2]
                        dependencies[pkg.lower()] = f"specified in go.mod ({version})"
    return dependencies


def extract_ruby_dependencies(repo_path):
    """
    Extracts dependencies from Gemfile.

    Parameters:
        repo_path (Path): Path to the Ruby repository.

    Returns:
        dict: Dependencies with their sources.
    """
    gemfile = repo_path / 'Gemfile'
    dependencies = {}
    if gemfile.exists():
        with open(gemfile, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('gem '):
                    parts = line.split(',')
                    gem_name = parts[0].split()[1].strip('"\'')
                    if gem_name:
                        dependencies[gem_name.lower()] = "specified in Gemfile"
    return dependencies


def extract_dependencies(project_types, repo_path):
    """
    Aggregates dependencies based on project types.

    Parameters:
        project_types (list): The types of the project.
        repo_path (Path): Path to the cloned repository.

    Returns:
        tuple: (dependencies dict, dev_dependencies dict, scripts dict)
    """
    dependencies = {}
    dev_dependencies = {}
    scripts = {}
    for project_type in project_types:
        if project_type == 'Node.js':
            deps, dev_deps, scr = extract_node_dependencies(repo_path)
            dependencies.update({k.lower(): v for k, v in deps.items()})
            dev_dependencies.update({k.lower(): v for k, v in dev_deps.items()})
            scripts.update(scr)
        elif project_type == 'Python':
            deps = extract_python_dependencies(repo_path)
            dependencies.update({k.lower(): v for k, v in deps.items()})
        elif project_type == 'Java':
            deps = extract_java_dependencies(repo_path)
            dependencies.update({k.lower(): v for k, v in deps.items()})
        elif project_type == 'Go':
            deps = extract_go_dependencies(repo_path)
            dependencies.update({k.lower(): v for k, v in deps.items()})
        elif project_type == 'Ruby':
            deps = extract_ruby_dependencies(repo_path)
            dependencies.update({k.lower(): v for k, v in deps.items()})
        elif project_type == 'Rust':
            # Implement Rust dependency extraction if needed
            pass
        # Add more project types as needed
    return dependencies, dev_dependencies, scripts


def detect_frameworks(project_types, dependencies):
    """
    Identifies common frameworks used in the project based on dependencies.

    Parameters:
        project_types (list): The types of the project.
        dependencies (dict): Dependencies of the project.

    Returns:
        list: List of detected frameworks.
    """
    frameworks = []
    for project_type in project_types:
        if project_type == 'Node.js':
            if 'react' in dependencies or 'react.js' in dependencies:
                frameworks.append('React')
            if 'vue' in dependencies or 'vue.js' in dependencies:
                frameworks.append('Vue.js')
            if 'angular' in dependencies or 'angular.js' in dependencies:
                frameworks.append('Angular')
            if 'express' in dependencies:
                frameworks.append('Express.js')
            if 'nestjs' in dependencies:
                frameworks.append('NestJS')
        elif project_type == 'Python':
            if 'fastapi' in dependencies:
                frameworks.append('FastAPI')
            if 'django' in dependencies:
                frameworks.append('Django')
            if 'flask' in dependencies:
                frameworks.append('Flask')
            if 'tornado' in dependencies:
                frameworks.append('Tornado')
        elif project_type == 'Java':
            if 'spring-boot' in dependencies.get('pom.xml', '').lower() or 'spring-boot' in dependencies.get('build.gradle', '').lower():
                frameworks.append('Spring Boot')
            if 'jakarta' in dependencies.get('pom.xml', '').lower():
                frameworks.append('Jakarta EE')
        elif project_type == 'Go':
            # Add Go frameworks if any
            pass
        elif project_type == 'Ruby':
            if 'rails' in dependencies.get('gemfile', '').lower() or 'rails' in dependencies:
                frameworks.append('Ruby on Rails')
            if 'sinatra' in dependencies:
                frameworks.append('Sinatra')
        elif project_type == 'Rust':
            # Add Rust frameworks if any
            pass
        # Add more as needed
    return frameworks


def parse_dockerfile(repo_path):
    """
    Extracts information from Dockerfile such as base image, exposed ports, environment variables, and volumes.

    Parameters:
        repo_path (Path): Path to the repository.

    Returns:
        dict: Dockerfile information.
    """
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
                env_vars = {k: v.strip() for k, v in env_matches}
                docker_info['Environment Variables'] = env_vars
            # Extract VOLUME
            volume_matches = re.findall(r'^VOLUME\s+\[?"?([^\]"]+)"?\]', content, re.MULTILINE)
            if volume_matches:
                docker_info['Volumes'] = volume_matches
    return docker_info


def parse_docker_compose(repo_path):
    """
    Parses docker-compose.yml to extract service details.

    Parameters:
        repo_path (Path): Path to the repository.

    Returns:
        dict: Docker Compose information.
    """
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
                logger.error(f"Error parsing docker-compose.yml: {exc}")
    return compose_info


def remove_helm_templates(content):
    """
    Removes Helm templating syntax from YAML content to make it parsable.

    Parameters:
        content (str): Raw YAML content.

    Returns:
        str: Cleaned YAML content.
    """
    # Remove all {{ ... }} patterns
    cleaned_content = re.sub(r'\{\{.*?\}\}', '', content)
    return cleaned_content


def parse_kubernetes_manifests(repo_path):
    """
    Parses Kubernetes YAML manifests to extract deployment and service information.
    Attempts to parse Helm templated YAML files by removing templating syntax.

    Parameters:
        repo_path (Path): Path to the repository.

    Returns:
        dict: Kubernetes manifests information.
    """
    kubernetes_info = {}
    yaml_parser = YAML()
    yaml_parser.preserve_quotes = True  # Preserve quotes if needed
    # Define directories to exclude
    exclude_dirs = ['examples', 'test', 'tests', 'docs']
    # Look for manifests in 'kubernetes/' directory or any '*.yaml' files
    possible_dirs = ['kubernetes', 'deployments', 'manifests']
    yaml_files = []
    for dir_name in possible_dirs:
        dir_path = repo_path / dir_name
        if dir_path.exists() and dir_path.is_dir():
            yaml_files.extend(dir_path.rglob('*.yaml'))
    # Additionally, include any YAML files in the root directory
    yaml_files.extend(repo_path.rglob('*.yaml'))
    # Filter out docker-compose.yml and exclude directories
    yaml_files = [
        f for f in yaml_files
        if f.name != 'docker-compose.yml' and not any(part in exclude_dirs for part in f.parts)
    ]
    for yaml_file in yaml_files:
        try:
            # Read the content
            with open(yaml_file, 'r') as f:
                content = f.read()
                # Check for Helm templating syntax
                if '{{' in content or '}}' in content:
                    logger.warning(f"Attempting to parse {yaml_file} with Helm templating syntax.")
                    # Preprocess the content to remove Helm templates
                    cleaned_content = remove_helm_templates(content)
                else:
                    cleaned_content = content
            # Attempt to parse the cleaned content
            data = yaml_parser.load_all(cleaned_content)
            for doc in data:
                if not doc:
                    continue
                if not isinstance(doc, dict):
                    logger.warning(f"Unexpected document format in {yaml_file}: {doc}")
                    continue
                kind = doc.get('kind')
                metadata = doc.get('metadata', {})
                name = metadata.get('name')
                if kind and name:
                    if kind not in kubernetes_info:
                        kubernetes_info[kind] = {}
                    kubernetes_info[kind][name] = doc
        except Exception as exc:
            logger.error(f"Error parsing {yaml_file}: {exc}")
    return kubernetes_info


def detect_external_dependencies(docker_compose_info, kubernetes_info):
    """
    Identifies external services based on Docker images and Kubernetes deployments.

    Parameters:
        docker_compose_info (dict): Docker Compose information.
        kubernetes_info (dict): Kubernetes manifests information.

    Returns:
        list: List of external dependencies.
    """
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
            if kind in ['Deployment', 'StatefulSet', 'DaemonSet']:
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
    """
    Scans Python files to identify imported modules.

    Parameters:
        repo_path (Path): Path to the Python repository.

    Returns:
        set: Set of imported module names.
    """
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
            logger.warning(f"Error parsing {file_path}: {e}")
    return dependencies_found


def scan_nodejs_imports(repo_path):
    """
    Scans Node.js files to identify imported modules using import and require statements.

    Parameters:
        repo_path (Path): Path to the Node.js repository.

    Returns:
        set: Set of imported module names.
    """
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
            logger.warning(f"Error reading {file_path}: {e}")
    return dependencies_found


def generate_missing_dependencies(project_types, dependencies, code_dependencies):
    """
    Identifies dependencies used in code but not declared in dependency files.

    Parameters:
        project_types (list): The types of the project.
        dependencies (dict): Declared dependencies.
        code_dependencies (set): Dependencies used in the code.

    Returns:
        dict: Missing dependencies with their descriptions.
    """
    missing = {}
    if 'Python' in project_types:
        declared = set(dependencies.keys())
        # Exclude standard library modules
        std_lib = {
            'base64', 'setuptools', 'typing', 'uuid', 'contextlib', 'logging',
            'json', 'os', 'io', 'collections', 're', 'enum', 'asyncio',
            'sys', 'math', 'itertools', 'datetime', 'random', 'time',
            'functools', 'operator', 'pathlib', 'hashlib', 'pickle',
            'threading', 'multiprocessing', 'socket', 'ssl', 'tempfile',
            'traceback', 'argparse', 'signal', 'struct', 'subprocess',
            'typing_extensions', 'weakref', 'types', 'sysconfig',
            'concurrent', 'operator', 'warnings', 'signal'
        }
        missing_deps = (code_dependencies - declared) - std_lib
        missing = {dep: "used in source code but not declared in requirements.txt" for dep in missing_deps}
    if 'Node.js' in project_types:
        declared = set(dependencies.keys())
        missing_deps = code_dependencies - declared
        missing = {dep: "used in source code but not declared in package.json" for dep in missing_deps}
    # Add more project types if needed
    return missing


def determine_layer(repo_url, master_list, management_repos):
    """
    Determines the layer (Platform, Domain, Applications, Management) of a repository based on the master_list.

    Parameters:
        repo_url (str): The repository URL.
        master_list (dict): The master list containing applications and repositories.
        management_repos (list): List of management repository URLs.

    Returns:
        str: The layer of the repository.
    """
    for app in master_list['applications']:
        # Check Platform Repositories
        if repo_url in app.get('platform_repos', []):
            return 'Platform'
        # Check Domain Specific Repositories
        if repo_url in app.get('domain_specific_repos', []):
            return 'Domain'
        # Check Frontend and Backend Repositories
        frontend = app['repositories'].get('frontend')
        backend = app['repositories'].get('backend')
        if repo_url == frontend or repo_url == backend:
            return 'Application'
    # Check if it's a management repository
    if repo_url in management_repos:
        return 'Management'
    # Default
    return 'Unknown'


def build_directory_tree(root_path, max_depth=4):
    """
    Builds a nested dictionary representing the directory tree up to a specified depth.

    Parameters:
        root_path (Path): The root directory path.
        max_depth (int): Maximum depth to traverse.

    Returns:
        dict: Nested dictionary representing the directory structure.
    """
    dir_tree = {}
    for current_path, dirs, files in os.walk(root_path):
        depth = len(current_path.relative_to(root_path).parts)
        if depth > max_depth:
            dirs[:] = []  # Don't recurse deeper
            continue
        parent = dir_tree
        for part in current_path.relative_to(root_path).parts:
            parent = parent.setdefault(part, {})
        for d in dirs:
            parent.setdefault(d, {})
        for f in files:
            parent.setdefault(f, None)
    return dir_tree


def map_subfolders(repo_path, repo_url, master_list):
    """
    Maps sub-folders within a repository to their respective components based on the directory structure.

    Parameters:
        repo_path (Path): Path to the cloned repository.
        repo_url (str): The repository URL.
        master_list (dict): The master list containing applications and repositories.

    Returns:
        dict: Mapping of sub-folders to components.
    """
    subfolder_mapping = {}
    for app in master_list['applications']:
        if repo_url == app['repositories']['backend']:
            # Example: Map sub-folders under 'spandaai-domain' to components
            domain_apps = ['edutech', 'hrtech', 'sportstech']
            for domain in domain_apps:
                domain_path = repo_path / 'spandaai-domain' / 'domain-applications' / domain
                if domain_path.exists():
                    subfolders = [f.name for f in domain_path.iterdir() if f.is_dir()]
                    subfolder_mapping[domain] = subfolders
    return subfolder_mapping


def generate_report(repos_info, output_path):
    """
    Writes the collected repository information to a JSON file.

    Parameters:
        repos_info (dict): Collected repository information.
        output_path (str): Path to the output JSON file.
    """
    try:
        with open(output_path, 'w') as f:
            json.dump(repos_info, f, indent=4)
        logger.info(f"Report generated at {output_path}")
    except IOError as e:
        logger.error(f"Error writing report to {output_path}: {e}")


def main():
    # Define your applications and their repositories
    master_list = {
        "applications": [
            {
                "name": "Dissertation Analysis",
                "description": "Analyze dissertations using AI-driven tools.",
                "type": "Edutech",
                "repositories": {
                    "frontend": "https://github.com/spandaai/dissertation-frontend",
                    "backend": "https://github.com/spandaai/Dissertation-Analysis"
                },
                "platform_repos": [
                    "https://github.com/spandaai/vllm.git",  # Corrected URL
                    "https://github.com/spandaai/ollama",
                    "https://github.com/spandaai/langchain",
                    "https://github.com/spandaai/kafka",
                    "https://github.com/spandaai/superset",
                    "https://github.com/weaviate/weaviate"
                ],
                "domain_specific_repos": [
                    "https://github.com/moodle/moodle"
                ]
            },
            {
                "name": "Variants of a Question Paper and Answers Generation",
                "description": "Generate multiple variants of question papers and answers.",
                "type": "Edutech",
                "repositories": {
                    "frontend": None,
                    "backend": "https://github.com/spandaai/Variants-of-a-Question-Paper"
                },
                "platform_repos": [
                    "https://github.com/spandaai/ollama",
                    "https://github.com/spandaai/langchain",
                    "https://github.com/weaviate/weaviate"
                ],
                "domain_specific_repos": [
                    "https://github.com/moodle/moodle"
                ]
            },
            {
                "name": "Current Instructor Evaluation",
                "description": "Evaluate instructors based on current metrics.",
                "type": "Edutech",
                "repositories": {
                    "frontend": None,
                    "backend": "https://github.com/spandaai/Current-Instructor-Evaluation"
                },
                "platform_repos": [
                    "https://github.com/spandaai/superset",
                    "https://github.com/spandaai/ollama",
                    "https://github.com/spandaai/langchain",
                    "https://github.com/weaviate/weaviate"
                ],
                "domain_specific_repos": [
                    "https://github.com/moodle/moodle"
                ]
            },
            {
                "name": "New Instructor Evaluation",
                "description": "Evaluate instructors based on new metrics.",
                "type": "Edutech",
                "repositories": {
                    "frontend": None,
                    "backend": "https://github.com/spandaai/New-Instructor-Evaluation"
                },
                "platform_repos": [
                    "https://github.com/spandaai/ollama",
                    "https://github.com/spandaai/langchain",
                    "https://github.com/spandaai/superset",
                    "https://github.com/weaviate/weaviate"
                ],
                "domain_specific_repos": [
                    "https://github.com/moodle/moodle"
                ]
            },
            {
                "name": "Automated Grading Assistant",
                "description": "Assist in automating the grading process using AI.",
                "type": "Edutech",
                "repositories": {
                    "frontend": None,
                    "backend": "https://github.com/spandaai/Automated-Grading-Assistant"
                },
                "platform_repos": [
                    "https://github.com/spandaai/ollama",
                    "https://github.com/spandaai/langchain",
                    "https://github.com/weaviate/weaviate"
                ],
                "domain_specific_repos": [
                    "https://github.com/moodle/moodle"
                ]
            },
            {
                "name": "ChatbotWILP",
                "description": "Provide chatbot functionalities for WILP.",
                "type": "Edutech",
                "repositories": {
                    "frontend": None,
                    "backend": "https://github.com/spandaai/ChatbotWILP"
                },
                "platform_repos": [
                    "https://github.com/spandaai/ollama",
                    "https://github.com/spandaai/langchain",
                    "https://github.com/weaviate/weaviate"
                ],
                "domain_specific_repos": [
                    "https://github.com/moodle/moodle"
                ]
            }
            # Add other applications following the same structure
            # ...
        ]
    }

    # Initialize a temporary directory for cloning
    temp_dir = Path('temp_repos_master')
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)

    repos_info = {}

    # Optionally, set authentication method
    # Uncomment and set your preferred authentication method if needed
    # auth_method = 'ssh'  # Options: None, 'ssh', 'pat'
    # auth_token = os.environ.get('GITHUB_PAT')  # If using PAT, ensure it's set as an environment variable
    auth_method = None
    auth_token = None

    # Set to track processed repositories to avoid duplication
    processed_repos = set()

    # Define repository to layer mapping for management repositories
    management_repos = [
        "https://github.com/spandaai/spandaai-management"
        # Add more management repositories if any
    ]

    for app in master_list['applications']:
        app_name = app['name']
        logger.info(f"Processing Application: {app_name}")
        repos_info[app_name] = {}
        repos_info[app_name]['Repository URL'] = {}
        repos_info[app_name]['Repository URL']['frontend'] = app['repositories']['frontend']
        repos_info[app_name]['Repository URL']['backend'] = app['repositories']['backend']
        repos_info[app_name]['Platform Repositories'] = app['platform_repos']
        repos_info[app_name]['Domain Specific Repositories'] = app['domain_specific_repos']
        repos_info[app_name]['Components'] = []
        # Collect all unique platform and domain-specific repos
        all_repos = set()
        if app['repositories']['frontend']:
            all_repos.add(app['repositories']['frontend'])
        if app['repositories']['backend']:
            all_repos.add(app['repositories']['backend'])
        for repo in app['platform_repos']:
            all_repos.add(repo)
        for repo in app['domain_specific_repos']:
            all_repos.add(repo)

        # Analyze each repository
        for repo_url in all_repos:
            if not repo_url:
                continue
            repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
            clone_dir = temp_dir / f"{repo_name}"

            # Check if repository is already processed to avoid duplication
            if repo_url in processed_repos:
                logger.info(f"Repository {repo_url} already processed. Skipping...")
                continue

            # Clone the repository
            success = clone_repo(repo_url, clone_dir, auth_method, auth_token)
            if not success:
                logger.warning(f"Skipping repository {repo_url} due to cloning error.\n")
                continue

            # Mark repository as processed
            processed_repos.add(repo_url)

            # Determine the layer
            layer = determine_layer(repo_url, master_list, management_repos)

            # Identify project types
            project_types = identify_project_type(clone_dir)
            dependencies, dev_dependencies, scripts = extract_dependencies(project_types, clone_dir)
            frameworks = detect_frameworks(project_types, dependencies)
            dockerfile = parse_dockerfile(clone_dir)
            docker_compose = parse_docker_compose(clone_dir)
            kubernetes_manifests = parse_kubernetes_manifests(clone_dir)
            external_deps = detect_external_dependencies(docker_compose, kubernetes_manifests)

            # Scan imports
            if 'Python' in project_types:
                code_dependencies = scan_python_imports(clone_dir)
            elif 'Node.js' in project_types:
                code_dependencies = scan_nodejs_imports(clone_dir)
            else:
                code_dependencies = set()

            # Identify missing dependencies
            missing_deps = generate_missing_dependencies(project_types, dependencies, code_dependencies)
            # Merge missing dependencies
            if missing_deps:
                dependencies.update(missing_deps)

            # Map sub-folders to components if needed
            subfolders = map_subfolders(clone_dir, repo_url, master_list)

            # Populate components
            component_entry = {
                "repository": repo_url,
                "layer": layer,
                "project_types": project_types,
                "frameworks": frameworks,
                "dependencies": dependencies,
                "dev_dependencies": dev_dependencies,
                "scripts": scripts,
                "dockerfile": dockerfile,
                "docker_compose": docker_compose,
                "kubernetes_manifests": kubernetes_manifests,
                "external_dependencies": external_deps,
                "subfolders": subfolders
            }
            repos_info[app_name]['Components'].append(component_entry)

        logger.info(f"Completed processing for {app_name}\n")

    # Handle management repositories separately
    for repo_url in management_repos:
        if not repo_url:
            continue
        repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
        clone_dir = temp_dir / f"{repo_name}"

        # Check if repository is already processed to avoid duplication
        if repo_url in processed_repos:
            logger.info(f"Repository {repo_url} already processed. Skipping...")
            continue

        # Clone the repository
        success = clone_repo(repo_url, clone_dir, auth_method, auth_token)
        if not success:
            logger.warning(f"Skipping repository {repo_url} due to cloning error.\n")
            continue

        # Mark repository as processed
        processed_repos.add(repo_url)

        # Determine the layer
        layer = 'Management'

        # Identify project types
        project_types = identify_project_type(clone_dir)
        dependencies, dev_dependencies, scripts = extract_dependencies(project_types, clone_dir)
        frameworks = detect_frameworks(project_types, dependencies)
        dockerfile = parse_dockerfile(clone_dir)
        docker_compose = parse_docker_compose(clone_dir)
        kubernetes_manifests = parse_kubernetes_manifests(clone_dir)
        external_deps = detect_external_dependencies(docker_compose, kubernetes_manifests)

        # Scan imports
        if 'Python' in project_types:
            code_dependencies = scan_python_imports(clone_dir)
        elif 'Node.js' in project_types:
            code_dependencies = scan_nodejs_imports(clone_dir)
        else:
            code_dependencies = set()

        # Identify missing dependencies
        missing_deps = generate_missing_dependencies(project_types, dependencies, code_dependencies)
        # Merge missing dependencies
        if missing_deps:
            dependencies.update(missing_deps)

        # Map sub-folders to components if needed
        subfolders = map_subfolders(clone_dir, repo_url, master_list)

        # Populate components
        component_entry = {
            "repository": repo_url,
            "layer": layer,
            "project_types": project_types,
            "frameworks": frameworks,
            "dependencies": dependencies,
            "dev_dependencies": dev_dependencies,
            "scripts": scripts,
            "dockerfile": dockerfile,
            "docker_compose": docker_compose,
            "kubernetes_manifests": kubernetes_manifests,
            "external_dependencies": external_deps,
            "subfolders": subfolders
        }

        # Add to a separate Management section
        management_app = "SpandaAI Management"
        if management_app not in repos_info:
            repos_info[management_app] = {
                "Repository URL": {},
                "Platform Repositories": [],
                "Domain Specific Repositories": [],
                "Components": []
            }
        repos_info[management_app]['Components'].append(component_entry)

    # Clean up cloned repositories
    try:
        shutil.rmtree(temp_dir)
        logger.info(f"Cleaned up temporary directory: {temp_dir}")
    except Exception as e:
        logger.error(f"Error cleaning up temporary directory {temp_dir}: {e}")

    # Generate Report
    output_report = 'bits_pilani_master_migration_report.json'
    generate_report(repos_info, output_report)

    # Print completion message
    logger.info("Introspection process completed successfully.")


if __name__ == "__main__":
    main()

