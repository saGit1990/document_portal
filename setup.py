from setuptools import setup, find_packages
setup(
    name="document_portal",
    version="0.1",
    author='suel abbasi and Iqra Khan',
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "pydantic",
        "langchain",
        "openai",
        "python-dotenv",
    ],
    
)
