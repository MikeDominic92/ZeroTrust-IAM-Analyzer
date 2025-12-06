# Contributing to ZeroTrust IAM Analyzer

Thank you for your interest in contributing to ZeroTrust IAM Analyzer! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help create a positive learning environment

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in Issues
2. Use the bug report template
3. Include:
   - Python version
   - OS and environment details
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages and logs

### Suggesting Enhancements

1. Open an issue with the enhancement label
2. Describe the use case and benefit
3. Provide examples if possible

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass: `pytest tests/`
6. Update documentation as needed
7. Commit with clear messages
8. Push to your fork
9. Open a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ZeroTrust-IAM-Analyzer.git
cd ZeroTrust-IAM-Analyzer

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt

# Frontend setup
cd ../frontend
npm install

# Run tests
cd ../backend
pytest tests/ -v
```

## Code Standards

### Python Style
- Follow PEP 8
- Use type hints where appropriate
- Write docstrings for functions and classes
- Maximum line length: 100 characters

### TypeScript/React
- Follow ESLint configuration
- Use TypeScript interfaces for props
- Write component documentation

### Testing
- Write unit tests for new features
- Maintain test coverage above 80%
- Use pytest fixtures for common setups

### Documentation
- Update README.md for user-facing changes
- Add docstrings to new functions
- Update API documentation for endpoint changes

## Project Structure

```
backend/
├── app/
│   ├── core/           # Configuration, database, auth
│   ├── models/         # SQLAlchemy models
│   ├── schemas/        # Pydantic schemas
│   └── src/
│       └── integrations/  # AWS, GCP integrations

frontend/
├── src/
│   ├── components/     # React components
│   ├── pages/          # Next.js pages
│   └── services/       # API clients
```

## Commit Message Guidelines

Use conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions or changes
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `chore`: Maintenance tasks

Example:
```
feat(aws): add IAM Access Analyzer integration

Implemented AWS Access Analyzer connector for external access detection.
Includes finding processor and policy validator.

Closes #15
```

## Adding New Cloud Integrations

1. Create integration class in `backend/app/src/integrations/`
2. Implement required methods:
   - `connect()`
   - `list_findings()`
   - `get_statistics()`
3. Add tests in `backend/tests/`
4. Update API endpoints if needed
5. Document in README

## Questions?

- Open a discussion in GitHub Discussions
- Tag issues with `question` label
- Reach out to maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
