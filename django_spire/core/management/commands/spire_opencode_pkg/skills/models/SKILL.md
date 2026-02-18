---
name: django-models
description: Best practice for working with Django models 
---

Use the following guidelines when working in models.py files.

# Important Patters
- Models are where we pull and organize information about our data structures.
- Methods on the model do NOT save the data! Any logic that processes or performs actions on the database lives in the service layer.
- Methods on the model can aggregate and display information related to the model.
- Breadcrumb classes are on the model. 
- Model names follow the hierarchy of the directory structure. For example, inventory_batch would have a batch module inside of the inventory module.

# Model Fields 

## Model Foreign Keys
- Foreign key relationships are always at the top of the model file sorted alphabetically. 
- The relationship is aways a string that is of format `'app_name.ModelName'`.
  - Review the related model apps.py file to find the app_label
- Do not import the related model.
- Foreign key relationships are always at the top of the model and formatted with line breaks.
- `related_name` It should read like English with the related model. Typically, it is the plural version but doesn't have to be.
  - readability is most important 
  - eg. product.batches.all() 
- `related_query_name` is the singular version of the word.
  - eg. Inventory.objects.filter(batch__name='Bin 4')

### Example
```python
class InventoryBatch(HistoryModelMixin, ActivityMixin):
    product = models.ForeignKey(
        'product.Product',
        on_delete=models.CASCADE,
        related_name='batches',
        related_query_name='batch'
    )
    
    location = models.ForeignKey(
        'inventory_location.InventoryLocation', # note here how the patter is app_name.ModelName. 
        on_delete=models.CASCADE,
        related_name='inventory',
        related_query_name='inventory',
        null=True,
        blank=True
    ) 

    name = models.CharField(max_length=255)
```

## Choice Fields
---
name: writing-model-choices
description: Writing choice classes using Django TextChoices 
---

### Best Practices
- The class name should be verbose
- Label is all capital letters and snakecase
- Code must be 3 characters
- When the label cannot be accurately translated, use the verbose implementation. 


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
