from setuptools import setup, find_packages

setup(
    name='questions-from-images',
    version='1.0',
    packages=find_packages(include=['services', 'test_scripts']),
    install_requires=[
        'fastapi==0.115.0',
        'uvicorn==0.31.0',
        'httpx==0.27.2',
        'pydantic==2.9.2',
        'asyncio',
        'langchain-text-splitters',
        'langchain',
        'aiohttp',
        'redis',
        'PyMuPDF==1.24.10',
        'python-docx==1.1.2',  
        'pytesseract==0.3.13',
        'Pillow==10.4.0',
        'requests==2.32.3',
        'python-dotenv',
        'python-multipart'
    ],
    entry_points={
        'console_scripts': [
            "qfi-start=api:main"  # Changed to point to api.py's main function
        ],
    },
    python_requires='>=3.8',
)