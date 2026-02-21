---
name: django-models
description: Best practice for working with Django models 
---

Use the following guidelines when working in models.py files.

# Best Practices

## Important Patters
- Models are where we pull and organize information about our data structures.
- Methods on the model do NOT save the data! Any logic that processes or performs actions on the database lives in the service layer.
- Methods on the model can aggregate and display information related to the model.
- Breadcrumb classes are on the model. 
- Model names follow the hierarchy of the directory structure. For example, inventory_batch would have a batch module inside of the inventory module.


### Example
```python
class InventoryBatch(HistoryModelMixin, ActivityMixin):
    inventory = models.ForeignKey(
        'inventory.Inventory',
        on_delete=models.CASCADE,
        related_name='batches',
        related_query_name='batch'
    )
    
    name = models.CharField(max_length=255)

    unit_of_measure = models.CharField(
        max_length=3, # must always be max length 3.
        choices=ProductUnitOfMeasureChoices.choices,
        default=ProductUnitOfMeasureChoices.LB
    )

    class Meta:
      verbose_name = 'Inventory Batch'
      verbose_name_plural = 'Inventory Batches'
      db_table = 'inventory_batch'
```


## Model Fields 

### Model Foreign Keys
- Foreign key relationships are always the first fields at the top of the model file sorted alphabetically. 
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
```

### Choice Fields
- Label is all capital letters and snakecase
- The tuple is (code, verbose_name). Code is always 3 characters.

### Example
```python
# app/product/choices.py
from django.db.models import TextChoices

class ProductTypeChoices(TextChoices):    
    RAW = 'raw', 'Raw'
    WORK_IN_PROGRESS = 'wip', 'Work in Progress'
    FINISHED_GOOD = 'fin', 'Finished Good'
```

```python
# app/product/models.py
from django.db import models
from app.product import choices


class Product(models.Model):

    unit_of_measure = models.CharField(
      max_length=3,
      choices=choices.ProductUnitOfMeasureChoices.choices,
      default=choices.ProductUnitOfMeasureChoices.LB
  )
```
