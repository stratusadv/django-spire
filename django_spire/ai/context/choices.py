from django.db.models import TextChoices


class PersonRoleChoices(TextChoices):
    ADMIN = 'admin', 'Admin'
    HUMAN_RESOURCES = 'human_resources', 'Human Resources'
    SALES = 'sales', 'Sales'
    MANAGER = 'manager', 'Manager'
    MARKETING = 'marketing', 'Marketing'
    TECHNICAL = 'technical', 'Technical'
    IT_SUPPORT = 'it_support', 'IT Support'
