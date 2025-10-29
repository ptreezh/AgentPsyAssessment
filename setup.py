from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="agentpsyassessment",
    version="1.0.0",
    author="Zhang",
    author_email="your-email@example.com",
    description="A portable psychological assessment framework using LLMs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ptreezh/AgentPsyAssessment",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Psychology",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "agentpsy-assess=llm_assessment.run_assessment_unified:main",
            "agentpsy-batch=llm_assessment.run_batch_suite:main",
            "agentpsy=cli:main",
        ],
    },
)