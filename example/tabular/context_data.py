from datetime import datetime
from random import randint, uniform
from uuid import uuid4


def tabular_context_data() -> dict:
    def generate_random_tabular_row():
        return {
            'uuid': str(uuid4()),
            'quantity': randint(1, 99),
            'cost': randint(1_000_000, 9_999_999),
            'price': int(randint(1_000_000, 9_999_999) * 1.30),
            'date': datetime.fromtimestamp(uniform(0, 4107580799)).isoformat()
        }
    context_data = {
        'rows': [
            {
                'data': generate_random_tabular_row(),
                'child_rows': [
                    {
                        'child_data': generate_random_tabular_row(),
                    } for _ in range(5)
                ]
            } for _ in range(10)
        ]
    }

    return context_data
