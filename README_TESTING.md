# VIN Decoder Bot - Testing Documentation

## Overview

This project includes a comprehensive testing suite with unit tests, integration tests, and end-to-end tests for the VIN Decoder Telegram Bot.

## Test Structure

```
src/tests/
├── conftest.py              # Pytest configuration and global fixtures
├── utils/
│   ├── factories.py         # Test data factories
│   └── helpers.py           # Test utilities and helpers
├── unit/
│   ├── domain/              # Domain layer tests
│   │   ├── test_vin_value_objects.py
│   │   ├── test_vehicle_entity.py
│   │   ├── test_user_entity.py
│   │   └── test_value_objects.py
│   ├── application/         # Application layer tests
│   │   ├── test_vehicle_application_service.py
│   │   ├── test_user_application_service.py
│   │   └── test_decode_vin_handler.py
│   ├── infrastructure/      # Infrastructure layer tests
│   │   ├── test_nhtsa_client.py
│   │   └── test_autodev_client.py
│   └── presentation/        # Presentation layer tests
│       └── test_command_handlers.py
├── integration/
│   ├── test_complete_flow.py
│   └── test_vehicle_decode_flow.py
└── e2e/
    ├── test_telegram_bot_flow.py
    └── test_bot_scenarios.py
```

## Installation

### Install Test Dependencies

```bash
# Install main dependencies
pip install -r requirements.txt

# Install test dependencies
pip install -r requirements-test.txt
```

## Running Tests

### Using Make Commands

```bash
# Run all tests
make test

# Run unit tests only
make test-unit

# Run integration tests only
make test-integration

# Run end-to-end tests only
make test-e2e

# Run tests with coverage report
make coverage

# Run code quality checks
make lint
make format
```

### Using Test Runner Script

```bash
# Run all tests
python run_tests.py --type all

# Run specific test type
python run_tests.py --type unit
python run_tests.py --type integration
python run_tests.py --type e2e

# Run with coverage
python run_tests.py --coverage

# Run tests in parallel
python run_tests.py --parallel 4

# Run tests matching keyword
python run_tests.py -k "test_vin"

# Stop on first failure
python run_tests.py --failfast
```

### Using Pytest Directly

```bash
# Run all tests
pytest src/tests

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest src/tests/unit/domain/test_vin_value_objects.py

# Run specific test
pytest src/tests/unit/domain/test_vin_value_objects.py::TestVINNumber::test_create_valid_vin

# Run tests with specific marker
pytest -m unit
pytest -m integration
pytest -m e2e

# Run tests in parallel
pytest -n 4

# Verbose output
pytest -vv
```

## Test Categories

### Unit Tests
- Test individual components in isolation
- Mock all external dependencies
- Fast execution (< 1 second per test)
- Located in `src/tests/unit/`

### Integration Tests
- Test interaction between components
- May use real implementations of some services
- Moderate execution time (< 5 seconds per test)
- Located in `src/tests/integration/`

### End-to-End Tests
- Test complete user scenarios
- Simulate real bot interactions
- Slower execution (< 10 seconds per test)
- Located in `src/tests/e2e/`

## Test Utilities

### Factories

The project includes comprehensive test factories for generating test data:

- **VINFactory**: Generate valid/invalid VIN numbers
- **UserFactory**: Create user entities with preferences
- **VehicleFactory**: Create vehicle entities with attributes
- **APIResponseFactory**: Mock API responses (NHTSA, AutoDev)
- **TelegramDataFactory**: Create Telegram update objects

Example usage:
```python
from src.tests.utils.factories import VINFactory, UserFactory

# Generate valid VIN
vin = VINFactory.create_valid_vin()

# Create user with custom preferences
user = UserFactory.create_user(
    telegram_id=123456789,
    username="testuser"
)

# Generate batch of VINs
vins = VINFactory.create_vin_batch(count=5, valid=True)
```

### Helpers

Test helpers provide utilities for common testing tasks:

- Mock HTTP responses
- Create Telegram bot mocks
- Async test utilities
- Time tracking for performance tests

Example usage:
```python
from src.tests.utils.helpers import (
    create_mock_telegram_update,
    create_mock_telegram_context,
    MockResponse
)

# Create mock Telegram update
update = create_mock_telegram_update(
    message=create_mock_telegram_message(text="/start")
)

# Create mock HTTP response
response = MockResponse(
    status_code=200,
    json_data={"success": True}
)
```

## Coverage

The test suite aims for >80% code coverage:

### Generate Coverage Report

```bash
# Terminal report
pytest --cov=src --cov-report=term-missing

# HTML report
pytest --cov=src --cov-report=html
# Open htmlcov/index.html in browser

# XML report (for CI/CD)
pytest --cov=src --cov-report=xml
```

### Coverage Goals
- Domain layer: >95%
- Application layer: >90%
- Infrastructure layer: >80%
- Presentation layer: >80%
- Overall: >85%

## Continuous Integration

### Pre-commit Checks

Run before committing:
```bash
make pre-commit
```

This runs:
1. Code formatting (black, isort)
2. Linting (flake8, mypy)
3. Fast test suite
4. Security checks

### CI Pipeline

The CI pipeline runs:
1. Install dependencies
2. Run linting and type checking
3. Run full test suite with coverage
4. Generate coverage reports
5. Run security scans

## Best Practices

1. **Write tests first**: Follow TDD when adding new features
2. **Keep tests independent**: Each test should be able to run in isolation
3. **Use descriptive names**: Test names should clearly describe what they test
4. **Mock external dependencies**: Unit tests should not make real API calls
5. **Test edge cases**: Include tests for error conditions and boundary values
6. **Maintain test data**: Use factories to generate consistent test data
7. **Regular test runs**: Run tests frequently during development
8. **Monitor coverage**: Ensure new code includes appropriate tests

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure all dependencies are installed
   ```bash
   pip install -r requirements-test.txt
   ```

2. **Async test failures**: Use `pytest-asyncio` fixtures
   ```python
   @pytest.mark.asyncio
   async def test_async_function():
       result = await async_function()
       assert result is not None
   ```

3. **Mock not working**: Ensure correct patch path
   ```python
   with patch('src.module.ClassName') as mock:
       # test code
   ```

4. **Slow tests**: Use markers to skip slow tests
   ```bash
   pytest -m "not slow"
   ```

## Contributing

When adding new features:

1. Write tests for the new functionality
2. Ensure all existing tests pass
3. Maintain or improve code coverage
4. Update test documentation if needed
5. Run the full test suite before submitting PR

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Python Testing Best Practices](https://realpython.com/python-testing/)
- [Test-Driven Development](https://martinfowler.com/bliki/TestDrivenDevelopment.html)
- [Mocking in Python](https://docs.python.org/3/library/unittest.mock.html)