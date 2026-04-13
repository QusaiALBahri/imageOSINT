# Contributing to ImageOSINT

First off, thank you for considering contributing to ImageOSINT! It's people like you that make this project such a great tool.

This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the [issue list](https://github.com/QusaiALBahri/imageOSINT/issues) as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps which reproduce the problem** in as many details as possible
* **Provide specific examples** to demonstrate the steps
* **Describe the behavior you observed** after following the steps
* **Expect which behavior you expected** to see instead and why
* **Include screenshots and animated GIFs** if possible
* **Include your environment details**: OS, Python version, dependencies versions
* **Include logs** if applicable

### Suggesting Enhancements

Enhancement suggestions are tracked as [GitHub issues](https://github.com/QusaiALBahri/imageOSINT/issues). When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title**
* **Provide a step-by-step description** of the suggested enhancement
* **Provide specific examples** to demonstrate the steps
* **Describe the current behavior** and **explain the expected behavior**
* **Explain why this enhancement would be useful**
* **List some other tools or applications** where this enhancement exists

### Pull Requests

* Fill in the required template
* Follow the [Python Style Guide](#python-style-guide)
* Include appropriate test cases
* Update documentation as needed
* End all files with a newline

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/imageOSINT.git
cd imageOSINT

# Add upstream remote
git remote add upstream https://github.com/QusaiALBahri/imageOSINT.git
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install all dependencies including dev tools
pip install -r requirements-backend.txt
pip install -e .
pip install pytest pytest-cov black flake8 mypy isort
```

### 4. Start Development Environment

```bash
# Using Docker Compose for development
docker-compose -f docker-compose.dev.yml up -d

# Or manually start required services
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=osint_password postgres:15-alpine
docker run -d -p 6379:6379 redis:7-alpine
```

### 5. Create Feature Branch

```bash
# Update main branch
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/my-amazing-feature
```

## Making Changes

### Code Style

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications.

### Python Style Guide

* **Indentation**: 4 spaces (not tabs)
* **Line length**: Maximum 100 characters
* **Imports**: Separate imports on different lines, organize using isort
* **Type hints**: Use type hints where possible
* **Docstrings**: Use Google-style docstrings
* **Comments**: Comment WHY, not WHAT

### Example Style

```python
"""Module docstring describing the module purpose."""

from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class MyClass:
    """Class docstring with clear description.
    
    Attributes:
        attr1 (str): Description of attr1
        attr2 (int): Description of attr2
    """

    def __init__(self, attr1: str, attr2: int) -> None:
        """Initialize MyClass.
        
        Args:
            attr1: Description of attr1
            attr2: Description of attr2
        """
        self.attr1 = attr1
        self.attr2 = attr2

    def my_method(self, param: str) -> Optional[Dict[str, Any]]:
        """Method description with clear purpose.
        
        Args:
            param: Parameter description
            
        Returns:
            Description of return value or None
            
        Raises:
            ValueError: When something is wrong
        """
        if not param:
            raise ValueError("param cannot be empty")
        
        logger.info(f"Processing {param}")
        return {"result": param}
```

### Formatting Code

```bash
# Format code with black
black .

# Sort imports with isort
isort . --profile black

# Check code style with flake8
flake8 . --max-line-length=100

# Type checking with mypy
mypy . --ignore-missing-imports
```

## Testing

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=backend --cov=core --cov=database --cov=tasks --cov-report=html

# Run specific test file
pytest tests/test_api.py -v

# Run specific test
pytest tests/test_api.py::test_register_user -v
```

### Writing Tests

```python
"""Test module for my_module."""

import pytest
from mymodule import MyClass


class TestMyClass:
    """Tests for MyClass."""

    @pytest.fixture
    def instance(self):
        """Create MyClass instance for testing."""
        return MyClass("test", 42)

    def test_initialization(self, instance):
        """Test MyClass initialization."""
        assert instance.attr1 == "test"
        assert instance.attr2 == 42

    def test_my_method(self, instance):
        """Test my_method returns expected result."""
        result = instance.my_method("input")
        assert result is not None
        assert "result" in result

    def test_my_method_raises_on_empty_param(self, instance):
        """Test my_method raises ValueError on empty param."""
        with pytest.raises(ValueError):
            instance.my_method("")
```

### Test Requirements

* Minimum 80% code coverage
* All public methods must have tests
* Edge cases should be covered
* Error conditions should be tested

## Commit Messages

* Use clear, descriptive commit messages
* Use imperative mood ("Add feature" not "Added feature")
* Keep the first line to 50 characters
* Reference issues and PRs after the first line
* Wrap body at 72 characters

### Example

```
Add authentication token refresh endpoint

- Implement /api/auth/refresh endpoint
- Add token validation middleware
- Add tests for token refresh flow
- Update API documentation

Fixes #123
Related to #456
```

## Pull Request Process

1. **Update your fork**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Push to your fork**
   ```bash
   git push origin feature/my-amazing-feature
   ```

3. **Create Pull Request**
   - Title: Clear and descriptive
   - Description: Fill in the PR template
   - Reference issues: Use "Fixes #123"
   - Link related discussions

4. **Respond to feedback**
   - Address all comments
   - Don't force push unless requested
   - Maintain discussion context

5. **Ensure CI passes**
   - All tests must pass
   - Code coverage must meet minimum
   - Linting checks must pass

## Review Process

All submissions require review. We use GitHub pull requests for this purpose. Consult [GitHub help](https://help.github.com/articles/about-pull-requests/) for more information.

### What We Look For

* **Code quality**: Clean, readable, maintainable code
* **Tests**: Comprehensive test coverage
* **Documentation**: Clear docs and comments
* **Breaking changes**: Minimized or clearly documented
* **Performance**: No significant performance regressions
* **Security**: No security vulnerabilities

## Additional Notes

### Issue and Pull Request Labels

* `bug`: Something isn't working
* `enhancement`: New feature or request
* `documentation`: Improvements or additions to documentation
* `good first issue`: Good for newcomers
* `help wanted`: Extra attention is needed
* `question`: Further information is requested
* `wontfix`: This will not be worked on

### Project Board

We use [GitHub Projects](https://github.com/QusaiALBahri/imageOSINT/projects) to track issues and PRs.

## Recognition

Contributors will be recognized in:
* README.md contributors list
* Release notes
* Hall of Fame

## Questions?

Feel free to open an issue with the `question` label or reach out to the maintainers.

## Resources

* [GitHub Help](https://help.github.com)
* [Pro Git Book](https://git-scm.com/book)
* [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
* [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

Thank you for contributing! 🎉
