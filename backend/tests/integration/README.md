# Phase A Integration Tests

Comprehensive integration tests for the Survey Collection System (Phase A).

## Overview

These tests verify the complete end-to-end workflow:
1. **Survey Creation** → Deployment to n8n
2. **Survey Submission** → Response collection
3. **Response Normalization** → Profile creation
4. **Database Persistence** → Query operations
5. **API Endpoints** → Request/response validation

## Test Structure

```
backend/tests/integration/
├── __init__.py                       # Package initialization
├── conftest.py                       # Shared pytest fixtures
├── test_phase_a_workflow.py          # Main workflow tests (8 scenarios)
├── test_api_flow.py                  # API endpoint tests
├── test_database_integration.py      # Database persistence tests
└── README.md                         # This file
```

## Test Files

### 1. conftest.py
Provides shared fixtures for all integration tests:
- **Sample Data**: 5 example user profiles (student, office worker, freelancer, parent, other)
- **Korean Data**: Korean language survey response
- **Invalid Data**: Various invalid inputs for validation testing
- **Mock Clients**: n8n, Supabase, FastAPI test clients
- **Performance Timer**: For benchmarking

### 2. test_phase_a_workflow.py
Main integration tests covering 8 scenarios:

#### Scenario 1: Survey Creation → Deployment
Tests survey template processing and n8n workflow deployment.

#### Scenario 2: Survey Submission → Response Storage
Tests form submission through webhook and database storage.

#### Scenario 3: Response Normalization → Profile Creation
Tests data processing pipeline and profile enrichment.

#### Scenario 4: Complete End-to-End Workflow
Tests full flow with 5 example users from survey to profile.

#### Scenario 5: Conditional Logic Testing
Tests subscription-based conditional fields (paper delivery options).

#### Scenario 6: Data Validation and Anomaly Detection
Tests validation catches errors (invalid email, future birth date, age < 13, etc.).

#### Scenario 7: Korean Localization
Tests Korean language support end-to-end.

#### Scenario 8: Multiple Submission Sources
Tests responses from n8n, Google Forms, and web form normalize correctly.

### 3. test_api_flow.py
API endpoint flow tests:
- Profile creation API
- Profile retrieval API
- Profile update API
- Survey submission API
- Bulk operations API
- Response time benchmarks
- Error handling
- CORS configuration
- Authentication (if enabled)

### 4. test_database_integration.py
Database persistence and query tests:
- Insert/update/delete operations
- Query by email, role, date range
- Database constraints (unique email, required fields, foreign keys)
- Index performance
- Transaction handling
- Backup/restore operations
- Security (RLS policies)

## Running Tests

### Run All Integration Tests
```bash
cd backend
pytest tests/integration/ -v
```

### Run Specific Test File
```bash
pytest tests/integration/test_phase_a_workflow.py -v
```

### Run Specific Test Class
```bash
pytest tests/integration/test_phase_a_workflow.py::TestCompleteEndToEndWorkflow -v
```

### Run Specific Test Method
```bash
pytest tests/integration/test_phase_a_workflow.py::TestCompleteEndToEndWorkflow::test_complete_phase_a_workflow -v
```

### Run with Coverage
```bash
pytest tests/integration/ --cov=src --cov-report=html --cov-report=term-missing
```

Output: `htmlcov/index.html`

### Run Performance Tests Only
```bash
pytest tests/integration/ -k "performance" -v
```

### Run with Detailed Output
```bash
pytest tests/integration/ -vv --tb=long
```

## Performance Benchmarks

Expected performance targets:

| Operation | Target | Test |
|-----------|--------|------|
| Survey creation | < 100ms | `test_survey_creation_performance` |
| Profile creation | < 1s | `test_profile_creation_from_response_performance` |
| API response | < 500ms | `test_api_response_time` |
| Email lookup (indexed) | < 100ms | `test_email_index_performance` |
| Role query | < 200ms | `test_role_index_performance` |

## Test Data Examples

### Student Profile
```python
{
    "name": "Lee Min-ji",
    "email": "minji@student.com",
    "birth_date": "2005-03-15",
    "role": "student",
    "personality_scores": [3, 4, 4, 4, 3, 4, 3, 3],
    "interests": ["education", "personal_growth", "career"],
    "subscription_type": "app_only"
}
```

### Office Worker Profile
```python
{
    "name": "Park Ji-hoon",
    "email": "jihoon@company.com",
    "birth_date": "1988-07-22",
    "role": "office_worker",
    "subscription_type": "hybrid",
    "paper_size": "A5",
    "delivery_frequency": "monthly"
}
```

### Korean Profile
```python
{
    "name": "김성훈",
    "email": "kim@example.com",
    "gender": "남성",
    "role": "직장인",
    "birth_location": "서울, 대한민국"
}
```

## Success Criteria

All tests passing indicates:
- ✅ Survey system fully operational
- ✅ Data normalization working correctly
- ✅ Profile creation pipeline validated
- ✅ End-to-end workflow verified
- ✅ Korean localization functional
- ✅ Validation catching all error cases
- ✅ Performance benchmarks met
- ✅ 85%+ code coverage
- ✅ Database operations working
- ✅ API endpoints responding correctly

## Troubleshooting

### Tests Fail with "Module Not Found"
```bash
# Ensure you're in the backend directory
cd backend

# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Verify Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Mock Clients Not Working
Ensure `conftest.py` is in the same directory. Pytest automatically loads fixtures from `conftest.py`.

### Async Tests Fail
Install `pytest-asyncio`:
```bash
pip install pytest-asyncio
```

### Coverage Not Generating
```bash
pip install pytest-cov
pytest tests/integration/ --cov=src --cov-report=html
```

### Database Connection Errors
These tests use **mocked** database clients by default. For real database testing:
1. Set up test Supabase instance
2. Update `conftest.py` with real credentials
3. Use `@pytest.fixture` to create/destroy test data

## Test Maintenance

### Adding New Test Scenarios
1. Add test method to appropriate test class
2. Use existing fixtures from `conftest.py`
3. Follow naming convention: `test_<scenario_description>`
4. Add docstring explaining what is tested
5. Assert expected behavior
6. Add print statement for success confirmation

### Adding New Fixtures
1. Add to `conftest.py`
2. Document purpose in docstring
3. Use `@pytest.fixture` decorator
4. Consider scope (`function`, `class`, `module`, `session`)

### Updating Test Data
Update examples in `conftest.py`:
- `EXAMPLE_STUDENT`
- `EXAMPLE_OFFICE_WORKER`
- `EXAMPLE_FREELANCER`
- `EXAMPLE_PARENT`
- `EXAMPLE_OTHER`
- `EXAMPLE_KOREAN_RESPONSE`

## Next Steps

After all integration tests pass:
1. Generate coverage report
2. Review uncovered code paths
3. Add missing test scenarios
4. Document any known limitations
5. Proceed to **Phase B: Personalization Engine**

## Related Documentation

- [Phase A Specification](../../../docs/tasks/WORKPLAN.md)
- [API Documentation](../../../docs/api/README.md)
- [Database Schema](../../../docs/database/SCHEMA.md)
- [n8n Workflow Guide](../../../docs/workflows/N8N_SETUP.md)

## Contact

For questions about integration tests, refer to the main project documentation or contact the development team.
