import requests
import pytest


@pytest.mark.parametrize(
    "category_name",
    ["Dogs", "Cats"]
)
def test_create_category(category_name):
    categories = requests.get('http://localhost:8000/categories').json()
    category_count = len(categories)
    created_category = requests.post(f'http://localhost:8000/categories/{category_name}').json()
    assert created_category['category'] == category_name
    categories = requests.get('http://localhost:8000/categories').json()
    assert len(categories) == category_count + 1


def test_get_categories():
    categories = requests.get('http://localhost:8000/categories').json()
    assert type(categories) == list
    assert type(categories[0]) == str


def test_update_category():
    categories = requests.get('http://localhost:8000/categories').json()
    original_category = categories[0]
    body = {'category': 'Mice'}
    updated_category = requests.patch(f'http://localhost:8000/categories/{original_category}', json=body).json()
    print(updated_category)
    assert updated_category['category'] == 'Mice'
    assert original_category not in requests.get('http://localhost:8000/categories').json()


def test_delete_category():
    categories = requests.get('http://localhost:8000/categories').json()
    assert len(categories) > 0
    while categories:
        category = categories.pop()
        requests.delete(f'http://localhost:8000/categories/{category}').json()
        remaining_categories = requests.get('http://localhost:8000/categories').json()
        assert len(remaining_categories) == len(categories)
        assert category not in remaining_categories

