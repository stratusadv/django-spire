---
name: seeding
description: Best practices for seeding django models 
---

# Django Seeding Best Practices

## Common Mistakes

### Model Choice Fields
- On django char fields that are linked to choices user faker.
- It will automatically pull from our selected choices.
```python
    fields = {
        'type': 'faker'
    }
```

### Overuser of faker
- Faker should be used to generate numerical data.
- Faker should be used for dates and type fields.
- Majority of the time we want to give the LLM context to generate us the best data.

### Foreign Key Relationships
- Field names must be appended with _id
- Only choose from the custom `fk_random` or `fk_in_order` methods when seeding
- The related objects must be imported.
- You cannot use a string for the model class import. It must be the direct import

```python
fields: ClassVar = {    
        'product_id': ('custom', 'fk_in_order', {'model_class': Product}),        
        'inventory_id': ('custom', 'fk_random', {'model_class': Invenotry}),        
    }
```

### Seeding Datetimes
- When seeding datetimes we need to use the `custom` `date_time_between`. This follow the same syntax as faker.
- Faker does not make the date times timezone aware. This is why we need to use this.

# Root seed.py import order
- It is very important to order our seed imports in a logical order.
- Modules depend on one another. Attempting to seed a dependent model before its relationship will result in data loss.

## Choose Appropriate Data Generation Strategies
Different data generation strategies serve different purposes:

### LLM (Large Language Models)
- Best for rich, human-like text content
- Automatically generates descriptive content for fields like descriptions
- Example: `("llm", "Describe this product for a sales catalog.")`

### Faker
- Ideal for realistic structured data (names, dates, numbers)
- Generates consistent, believable data for fields like names, addresses, and dates
- Example: `("faker", "word")` or `("faker", "date_time_between", {"start_date": "-30d", "end_date": "now"})`

### Static
- Use for consistent values like feature flags or test conditions
- Provides the same value every time for predictable results
- Example: `("static", True)` or `"in_stock": True`

### Callable
- For dynamic behavior like timestamps or context-aware generation
- Executes a function at runtime to generate values
- Example: `("callable", lambda: timezone.now())`

### Custom
- For reusable methods like sequential foreign key assignment
- Critical for maintaining referential integrity in foreign key relationships
- Example: `("custom", "in_order", {"values": supplier_ids})`
- Important: When using custom methods for foreign keys, ensure proper caching to maintain data consistency

## Configure Default Behavior Appropriately
```python
class ProductSeeder(DjangoModelSeeder):
    model_class = Product
    default_to = "llm"  # Options: 'llm', 'faker'
```

## Field Configuration Patterns

### Basic Field Definitions
```python
fields = {
    'id': 'exclude',
    'name': ('llm', 'A product in a clothing sales catalog'),
    'description': ('llm', 'Describe this product for a clothing sales catalog.'),
    'price': ('faker', 'pydecimal', {'left_digits': 2, 'right_digits': 2, 'positive': True}),
    'in_stock': True,
    'created_at': ('faker', 'date_time_between', {'start_date': '-30d', 'end_date': 'now'}),
    'updated_at': lambda: timezone.now(),
    'supplier_id': ('custom', 'in_order', {'values': supplier_ids})
}
```

### Advanced Field Types
- **Faker**: Use for quick realistic structured data
- **LLM**: Generate rich text content. Used in most cases.
- **Static**: Fixed values for consistency
- **Callable**: Dynamic runtime evaluation
- **Custom**: Reusable methods for complex logic, especially foreign key relationships


# Implementation Guidelines

### 1. Cache Configuration
Always configure caching for frequently-used seeders:
```python
class ProductSeeder(DjangoModelSeeder):
    cache_name = 'product_seeder'
    cache_seed = True
```

### 2. Field Selection Strategy
- Use `default_to = "llm"` or `"faker"` for automatic field population
- Explicitly define fields that should be excluded


### 3. Review the model
- Review the model the seeder class links to.
- All fields on the model should also be on the seeder.

### 4. Build the fields dictionary
- Decide the field types needed to build the most realistic data structures.

### 5. Custom Methods Usage
Leverage built-in custom methods for common patterns:
- `in_order`: Sequential value assignment for maintaining data relationships
- `date_time_between`: Random date generation within ranges
- `fk_random`: Random foreign key selection from existing records
- `fk_in_order`: Sequential foreign key assignment for maintaining referential integrity

### 6. Module seed.py
- Update the seed.py field for the module
- Use `seed()` for object instantiation without DB insertion
- Use `seed_database()` for direct database insertion
- Combine with field overrides for edge case testing
- When overriding fields in seed methods, you can customize base seeders for specific use cases

### 7. Project seed.py
- Ensure the seed.py we just configured is important in the project root seed.py


## Edge Case Seeding
Override fields to create specific test scenarios:
```python
ProductSeeder.seed(
    count=1,
    fields={"in_stock":  False}
)
```

Create specialized class methods that need to be re-used:
```python
class ProductSeeder(DjangoModelSeeder):
    @classmethod
    def seed_grocery_product(cls, count: int = 1):
        cls.seed_database(
            count=count,
            fields=cls.fields | {
                'name': ('llm', 'Grocery product name'),
                'description': ('llm', 'Grocery product description'),
            }
        ) 
```

## Seeding in specific orders
- When building class methods, chain calls down the dependency hierarchy to keep modularity.
- Each Seeder class is responsible for creating its model. 
- In the example below, I can call ProductSeeder.seed_with_inventory(count=20) and it generates all the inventory batches and inventory objects with the correct relationships.
- Only the parent seeder will be in our project root seed.py.
```python
# Product Seeder needs to link to batches and inventory

class ProductSeeder(DjangoModelSeeder):
    ... 
    
    @classmethod
    def seed_with_inventory(cls, count: int = 1):
        products = cls.seed_database(count=count)

        for product in products:
            BatchSeeder.seed_by_product(
                product=product,
                count=2,
            )

        return products



class BatchSeeder(DjangoModelSeeder):
    ... 
    @classmethod
    def seed_by_product(
            cls,
            product: Product,
            count: int = 1
    ):
        batches =  cls.seed_database(
            count=count,
            fields={
                'product_id': product.id
            }
        )

        for batch in batches:
            InventorySeeder.seed_database(
                count=3,
                fields={
                    'product_id': product.id,
                    'batch_id': batch.id
                }
            )

        return batches
    
    class InventorySeeder(DjangoModelSeeder):
     ...
    @classmethod
    def seed_by_product_and_batch(cls, product, batch, count: int = 1):
        """
        Seed inventory items specifically for a given product and batch.
        This ensures proper relationship with both product and batch.
        """
        return cls.seed_database(
            count=count,
            fields={
                'product_id': product.id,
                'batch_id': batch.id
            }
        )
```
