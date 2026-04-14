---
name: writing-model-choices
description: Writing choice classes using Django TextChoices 
---

# Instructions
1. Navigate to the correct directory
2. Create a choices.py file if it does not exist
3. Define your choice class using Django's TextChoices


## Best Practices
- The class name should be verbose
- Label is all capital letters and snakecase
- Code must be 3 characters
- When the label cannot be accurately translated, use the verbose implementation. 

## Examples

### Basic Implementation
This should cover most use cases.
```python
from django.db.models import TextChoices

class ProductTypeChoices(TextChoices):
    RAW = 'raw'
    WORK_IN_PROGRESS = 'wip'
    FINISHED_GOOD = 'fin'
```

### Verbose Implementation
Use when we need to specifically define the text output of the label.

```python
from django.db.models import TextChoices

class ProductTypeChoices(TextChoices):
    RAW = 'raw', 'Raw'
    WORK_IN_PROGRESS = 'wip', 'Work in Progress'
    FINISHED_GOOD = 'fin', 'Finished Good'
```

### Model Implementation 
- The max length must always match the code length. If implemented properly, it will be 3.

```python
from django.db import models
class Product(models.Model):

    unit_of_measure = models.CharField(
        max_length=3,
        choices=ProductUnitOfMeasureChoices.choices,
        default=ProductUnitOfMeasureChoices.LB
    )

```