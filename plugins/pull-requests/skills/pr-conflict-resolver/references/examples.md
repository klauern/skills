# Conflict Resolution Examples

## Example 1: Import Ordering (Auto-Resolve)

**Conflict**:
```python
<<<<<<< HEAD
import os
import sys
from typing import Dict, List
=======
from typing import Dict, List
import os
import sys
>>>>>>> feature/add-types
```

**Analysis**: Same imports, different order → Auto-resolve with PEP 8 sorting

**Resolution**:
```python
import os
import sys
from typing import Dict, List
```

**Command**: `git add file.py` (auto-resolved)

---

## Example 2: Function Signature Change (Suggest Strategy)

**Conflict**:
```python
<<<<<<< HEAD
def create_user(email: str, password: str, role: str = 'user'):
    user = User(email=email, password=hash_password(password), role=role)
    return user
=======
def create_user(email: str, password: str):
    user = User(email=email, password=hash_password(password))
    send_welcome_email(user)
    return user
>>>>>>> feature/welcome-email
```

**Analysis**:
- HEAD: Added role parameter
- Feature: Added welcome email
- Both valuable, merge needed

**Resolution**:
```python
def create_user(email: str, password: str, role: str = 'user'):
    user = User(email=email, password=hash_password(password), role=role)
    send_welcome_email(user)
    return user
```

**Follow-up**: Check call sites for new `role` parameter

---

## Example 3: Refactoring Conflict (Manual Guidance)

**Conflict**:
```python
<<<<<<< HEAD
class Order:
    def __init__(self, order_id):
        self.payment_processor = PaymentProcessor()  # Extracted

    def process_payment(self, amount):
        return self.payment_processor.process(self.order_id, amount)
=======
class Order:
    def __init__(self, order_id):
        self.status = 'pending'

    def cancel_payment(self):  # New feature
        if self.status == 'paid':
            self.status = 'refunded'
            return True
        return False
>>>>>>> feature/payment-cancel
```

**Analysis**:
- HEAD: Refactored to composition pattern
- Feature: Added cancel method to old structure
- Must adapt feature to new architecture

**Resolution**:
```python
class Order:
    def __init__(self, order_id):
        self.payment_processor = PaymentProcessor()

    def process_payment(self, amount):
        return self.payment_processor.process(self.order_id, amount)

    def cancel_payment(self):
        return self.payment_processor.cancel(self.order_id)
```

**Follow-up**: Add `cancel()` method to `PaymentProcessor` class

---

## Example 4: Logic Conflict (Choose with Guidance)

**Conflict**:
```python
<<<<<<< HEAD
def search_users(query: str, limit: int = 10):
    """Database full-text search."""
    return db.query(User).filter(
        User.name.ilike(f'%{query}%')
    ).limit(limit).all()
=======
def search_users(query: str, limit: int = 10):
    """Elasticsearch search."""
    results = es.search(index='users', body={
        'query': {'match': {'name': query}},
        'size': limit
    })
    return [User.from_es(hit) for hit in results['hits']['hits']]
>>>>>>> feature/elasticsearch
```

**Analysis**:
- HEAD: Database search (simpler, no infra)
- Feature: Elasticsearch (scalable, faster)
- Choose based on project needs

**Options**:
1. **Small scale**: Keep database search
2. **Large scale**: Use Elasticsearch
3. **Migration path**: Feature flag for both

**Resolution (Option 3)**:
```python
def search_users(query: str, limit: int = 10):
    if settings.USE_ELASTICSEARCH:
        return _search_users_es(query, limit)
    return _search_users_db(query, limit)
```

---

## Resolution Summary

| Example | Type | Strategy | Auto-Fix |
|---------|------|----------|----------|
| Import ordering | Simple | Sort by convention | ✅ |
| Signature change | Medium | Merge both changes | ⚠️ |
| Refactoring | Complex | Adapt to new structure | ❌ |
| Logic conflict | Complex | Choose or feature flag | ❌ |
