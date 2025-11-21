# Example Conflict Resolutions

This document provides real-world examples of merge conflict resolutions using the pr-conflict-resolver skill.

## Example 1: Import Ordering

### Scenario

Both branches added imports but in different order.

### Conflict

```python
# src/models/user.py
<<<<<<< HEAD
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional
=======
from typing import Dict, List, Optional
from datetime import datetime
import os
import sys
>>>>>>> feature/add-type-hints
```

### Analysis

**Conflict Type**: Import ordering (Simple)

**Intent**:
- HEAD: Added imports as needed
- feature/add-type-hints: Reorganized imports per PEP 8

**Resolution Strategy**: Auto-resolve using PEP 8 rules

### Resolution

```python
# Automatically resolved per PEP 8:
# 1. Standard library imports (alphabetical)
# 2. Related third-party imports
# 3. Local imports

import os
import sys
from datetime import datetime
from typing import Dict, List, Optional
```

### Commands

```bash
# Auto-resolved by skill
git add src/models/user.py
```

---

## Example 2: Function Signature Conflict

### Scenario

Main branch added a parameter to a function, while feature branch added calls to the old function signature.

### Conflict

```python
# src/services/user_service.py
<<<<<<< HEAD
def create_user(email: str, password: str, role: str = 'user'):
    """Create a new user with specified role."""
    user = User(email=email, password=hash_password(password), role=role)
    return user
=======
def create_user(email: str, password: str):
    """Create a new user."""
    user = User(email=email, password=hash_password(password))
    send_welcome_email(user)  # New functionality added
    return user
>>>>>>> feature/welcome-email
```

### Analysis

**Conflict Type**: Function signature change (Medium)

**Intent**:
- HEAD: Added role parameter for role-based access control
- feature/welcome-email: Added welcome email functionality

**Both changes are valuable**: Need to combine them

**Resolution Strategy**: Merge both changes

### Resolution

```python
def create_user(email: str, password: str, role: str = 'user'):
    """Create a new user with specified role."""
    user = User(email=email, password=hash_password(password), role=role)
    send_welcome_email(user)  # Keep from feature branch
    return user
```

### Additional Work

Need to update call sites in feature branch:

```bash
# Find call sites
git grep "create_user(" -- "*.py"

# Update each call site to include role parameter if needed
# or rely on default value
```

### Commands

```bash
# After resolving
git add src/services/user_service.py
```

---

## Example 3: Refactoring Conflict

### Scenario

Main branch refactored a class to use composition, while feature branch added methods to the original class structure.

### Conflict

```python
# src/models/order.py
<<<<<<< HEAD
class Order:
    def __init__(self, order_id: str):
        self.order_id = order_id
        self.payment_processor = PaymentProcessor()  # Extracted to separate class

    def process_payment(self, amount: float):
        return self.payment_processor.process(self.order_id, amount)
=======
class Order:
    def __init__(self, order_id: str):
        self.order_id = order_id
        self.status = 'pending'

    def process_payment(self, amount: float):
        # Original inline implementation
        if self.validate_payment(amount):
            self.status = 'paid'
            return True
        return False

    def cancel_payment(self):
        """New method added in feature branch."""
        if self.status == 'paid':
            self.status = 'refunded'
            return True
        return False
>>>>>>> feature/payment-cancellation
```

### Analysis

**Conflict Type**: Refactoring conflict (Complex)

**Intent**:
- HEAD: Extracted payment logic to separate class (better separation of concerns)
- feature/payment-cancellation: Added payment cancellation feature

**Resolution Strategy**: Adapt new feature to refactored structure

### Resolution

```python
class Order:
    def __init__(self, order_id: str):
        self.order_id = order_id
        self.payment_processor = PaymentProcessor()

    def process_payment(self, amount: float):
        return self.payment_processor.process(self.order_id, amount)

    def cancel_payment(self):
        """Adapted to use refactored payment processor."""
        return self.payment_processor.cancel(self.order_id)
```

### Additional Work

Update PaymentProcessor class to include cancel method:

```python
# src/services/payment_processor.py
class PaymentProcessor:
    def process(self, order_id: str, amount: float):
        # ... existing code

    def cancel(self, order_id: str):
        """Cancel payment for order."""
        # Implement cancellation logic
        order = get_order(order_id)
        if order.status == 'paid':
            order.status = 'refunded'
            return True
        return False
```

### Commands

```bash
git add src/models/order.py
git add src/services/payment_processor.py
```

---

## Example 4: Logic Conflict

### Scenario

Both branches implemented the same feature (user search) differently.

### Conflict

```python
# src/api/search.py
<<<<<<< HEAD
def search_users(query: str, limit: int = 10):
    """Search users using database full-text search."""
    return db.session.query(User).filter(
        User.name.ilike(f'%{query}%') |
        User.email.ilike(f'%{query}%')
    ).limit(limit).all()
=======
def search_users(query: str, limit: int = 10):
    """Search users using Elasticsearch."""
    results = es.search(
        index='users',
        body={
            'query': {
                'multi_match': {
                    'query': query,
                    'fields': ['name^2', 'email', 'bio']
                }
            },
            'size': limit
        }
    )
    return [User.from_es(hit) for hit in results['hits']['hits']]
>>>>>>> feature/elasticsearch-search
```

### Analysis

**Conflict Type**: Logic conflict (Complex)

**Intent**:
- HEAD: Simple database search (quick to implement, good enough for small datasets)
- feature/elasticsearch-search: Advanced search with Elasticsearch (better performance, more features)

**Trade-offs**:
- Database: Simpler, no additional infrastructure
- Elasticsearch: More powerful, requires setup and maintenance

### User Guidance

```markdown
## Conflict Analysis

**Location**: src/api/search.py:15-32

**Our Approach** (HEAD):
- Uses database full-text search with LIKE queries
- Searches name and email fields
- Pros: Simple, no additional dependencies
- Cons: Slower for large datasets, limited search capabilities

**Their Approach** (feature/elasticsearch-search):
- Uses Elasticsearch for full-text search
- Searches name, email, and bio with field boosting
- Pros: Fast, scalable, advanced features
- Cons: Requires Elasticsearch setup

**Recommendation**:
Choose based on your scale and requirements:

**Option 1** - Small/Medium dataset (<100k users):
  Keep database search (HEAD) - simpler deployment

**Option 2** - Large dataset or need advanced search:
  Use Elasticsearch (feature/elasticsearch-search)

**Option 3** - Support both with feature flag:
  Allow gradual migration from DB to ES
```

### Resolution (Option 3: Both with feature flag)

```python
def search_users(query: str, limit: int = 10):
    """Search users using configured search backend."""
    if settings.USE_ELASTICSEARCH:
        return _search_users_es(query, limit)
    else:
        return _search_users_db(query, limit)

def _search_users_db(query: str, limit: int):
    """Search users using database full-text search."""
    return db.session.query(User).filter(
        User.name.ilike(f'%{query}%') |
        User.email.ilike(f'%{query}%')
    ).limit(limit).all()

def _search_users_es(query: str, limit: int):
    """Search users using Elasticsearch."""
    results = es.search(
        index='users',
        body={
            'query': {
                'multi_match': {
                    'query': query,
                    'fields': ['name^2', 'email', 'bio']
                }
            },
            'size': limit
        }
    )
    return [User.from_es(hit) for hit in results['hits']['hits']]
```

### Commands

```bash
git add src/api/search.py

# Add configuration setting
git add src/config/settings.py

# Run tests
pytest tests/test_search.py
```

---

## Example 5: Dependency Version Conflict

### Scenario

Both branches updated the same dependency to different versions.

### Conflict

```json
// package.json
{
  "dependencies": {
<<<<<<< HEAD
    "lodash": "^4.17.21",
=======
    "lodash": "^4.17.20",
>>>>>>> feature/update-dependencies
    "react": "^18.0.0"
  }
}
```

### Analysis

**Conflict Type**: Version conflict (Medium)

**Intent**:
- HEAD: Updated to 4.17.21 (security patch)
- feature/update-dependencies: Updated to 4.17.20

**Resolution Strategy**: Choose newer version (4.17.21)

### Resolution

```json
{
  "dependencies": {
    "lodash": "^4.17.21",
    "react": "^18.0.0"
  }
}
```

### Commands

```bash
# Update lock file
npm install

# Verify no breaking changes
npm test

git add package.json package-lock.json
```

---

## Example 6: Configuration Conflict

### Scenario

Both branches added different configuration options.

### Conflict

```yaml
# config/settings.yml
database:
  host: localhost
  port: 5432
<<<<<<< HEAD
  pool_size: 10
  timeout: 30
=======
  ssl_mode: require
  connection_timeout: 60
>>>>>>> feature/secure-db-connection
```

### Analysis

**Conflict Type**: Non-overlapping additions (Simple)

**Intent**:
- HEAD: Added connection pool settings
- feature/secure-db-connection: Added SSL and timeout settings

**Resolution Strategy**: Merge both (combine non-overlapping changes)

### Resolution

```yaml
database:
  host: localhost
  port: 5432
  pool_size: 10
  timeout: 30
  ssl_mode: require
  connection_timeout: 60
```

### Commands

```bash
git add config/settings.yml

# Verify configuration is valid
python -c "import yaml; yaml.safe_load(open('config/settings.yml'))"
```

---

## Example 7: Test Conflict

### Scenario

Both branches added tests for the same function but testing different aspects.

### Conflict

```python
# tests/test_user.py
def test_create_user():
<<<<<<< HEAD
    """Test user creation with valid data."""
    user = create_user('test@example.com', 'password123')
    assert user.email == 'test@example.com'
    assert user.password != 'password123'  # Should be hashed
=======
    """Test user creation with invalid email."""
    with pytest.raises(ValueError):
        create_user('invalid-email', 'password123')
>>>>>>> feature/email-validation
```

### Analysis

**Conflict Type**: Non-overlapping test additions (Simple)

**Intent**:
- HEAD: Tests successful user creation
- feature/email-validation: Tests email validation error handling

**Resolution Strategy**: Merge both into separate test functions

### Resolution

```python
def test_create_user_success():
    """Test user creation with valid data."""
    user = create_user('test@example.com', 'password123')
    assert user.email == 'test@example.com'
    assert user.password != 'password123'  # Should be hashed

def test_create_user_invalid_email():
    """Test user creation with invalid email."""
    with pytest.raises(ValueError):
        create_user('invalid-email', 'password123')
```

### Commands

```bash
git add tests/test_user.py

# Run tests
pytest tests/test_user.py -v
```

---

## Example 8: Documentation Conflict

### Scenario

Both branches updated the same documentation section differently.

### Conflict

```markdown
# README.md
## Installation

<<<<<<< HEAD
1. Clone the repository
2. Install dependencies: `npm install`
3. Set up environment variables (see `.env.example`)
4. Run migrations: `npm run migrate`
5. Start the server: `npm start`
=======
### Prerequisites

- Node.js 18+
- PostgreSQL 14+
- Redis 6+

### Steps

1. Clone the repository
2. Install dependencies: `npm install`
3. Start the server: `npm start`
>>>>>>> feature/improve-docs
```

### Analysis

**Conflict Type**: Documentation update (Medium)

**Intent**:
- HEAD: Added migration step (important!)
- feature/improve-docs: Added prerequisites section (better structure)

**Resolution Strategy**: Merge both improvements

### Resolution

```markdown
## Installation

### Prerequisites

- Node.js 18+
- PostgreSQL 14+
- Redis 6+

### Steps

1. Clone the repository
2. Install dependencies: `npm install`
3. Set up environment variables (see `.env.example`)
4. Run migrations: `npm run migrate`
5. Start the server: `npm start`
```

### Commands

```bash
git add README.md
```

---

## Summary of Resolution Patterns

| Conflict Type | Example | Strategy | Complexity |
|--------------|---------|----------|------------|
| Import ordering | Example 1 | Auto-resolve | Simple |
| Function signature | Example 2 | Merge both | Medium |
| Refactoring | Example 3 | Adapt to new structure | Complex |
| Logic implementation | Example 4 | Choose or combine with flag | Complex |
| Dependency version | Example 5 | Choose newer | Medium |
| Configuration | Example 6 | Merge both | Simple |
| Test additions | Example 7 | Separate test functions | Simple |
| Documentation | Example 8 | Merge improvements | Medium |

## Key Takeaways

1. **Simple conflicts** (import order, config additions) can be auto-resolved
2. **Medium conflicts** (signatures, versions) need strategy selection but are straightforward
3. **Complex conflicts** (logic, refactoring) require understanding intent and may need refactoring
4. **Always verify** resolutions with tests and code review
5. **Document** complex resolution decisions for future reference
6. **Prefer combining** both changes when possible over choosing one side
7. **Consider long-term** implications, not just immediate merge success
