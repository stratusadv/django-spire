from __future__ import annotations

from unittest import TestCase

from django_spire.core.tag.tools import (
    get_matching_a_percentage_from_tag_sets,
    get_matching_b_percentage_from_tag_sets,
    get_matching_count_from_tag_sets,
    get_matching_tag_set_from_tag_sets,
    get_score_percentage_from_tag_set_weighted,
    simplify_and_weight_tag_set_to_dict,
    simplify_tag_set,
    simplify_tag_set_to_list,
)


class TestGetMatchingTagSetFromTagSets(TestCase):
    def test_full_intersection(self) -> None:
        tag_set_a = {'apple', 'banana', 'orange'}
        tag_set_b = {'apple', 'banana', 'orange'}

        result = get_matching_tag_set_from_tag_sets(tag_set_a, tag_set_b)

        assert result == {'apple', 'banana', 'orange'}

    def test_no_intersection(self) -> None:
        tag_set_a = {'apple', 'banana', 'orange'}
        tag_set_b = {'grape', 'kiwi', 'pear'}

        result = get_matching_tag_set_from_tag_sets(tag_set_a, tag_set_b)

        assert result == set()

    def test_partial_intersection(self) -> None:
        tag_set_a = {'apple', 'banana', 'orange'}
        tag_set_b = {'apple', 'grape', 'kiwi'}

        result = get_matching_tag_set_from_tag_sets(tag_set_a, tag_set_b)

        assert result == {'apple'}


class TestGetMatchingCountFromTagSets(TestCase):
    def test_full_match(self) -> None:
        tag_set_a = {'apple', 'banana'}
        tag_set_b = {'apple', 'banana'}

        assert get_matching_count_from_tag_sets(tag_set_a, tag_set_b) == 2

    def test_no_match(self) -> None:
        tag_set_a = {'apple', 'banana'}
        tag_set_b = {'grape', 'kiwi'}

        assert get_matching_count_from_tag_sets(tag_set_a, tag_set_b) == 0

    def test_partial_match(self) -> None:
        tag_set_a = {'apple', 'banana', 'orange'}
        tag_set_b = {'apple', 'grape'}

        assert get_matching_count_from_tag_sets(tag_set_a, tag_set_b) == 1


class TestGetMatchingAPercentageFromTagSets(TestCase):
    def test_empty_tag_set_a(self) -> None:
        tag_set_a = set()
        tag_set_b = {'apple', 'banana'}

        assert get_matching_a_percentage_from_tag_sets(tag_set_a, tag_set_b) == 0.0

    def test_full_match(self) -> None:
        tag_set_a = {'apple', 'banana'}
        tag_set_b = {'apple', 'banana', 'orange'}

        assert get_matching_a_percentage_from_tag_sets(tag_set_a, tag_set_b) == 1.0

    def test_partial_match(self) -> None:
        tag_set_a = {'apple', 'banana', 'orange'}
        tag_set_b = {'apple'}

        assert abs(get_matching_a_percentage_from_tag_sets(tag_set_a, tag_set_b) - 0.333) < 0.01


class TestGetMatchingBPercentageFromTagSets(TestCase):
    def test_empty_tag_set_b(self) -> None:
        tag_set_a = {'apple', 'banana'}
        tag_set_b = set()

        assert get_matching_b_percentage_from_tag_sets(tag_set_a, tag_set_b) == 0.0

    def test_full_match(self) -> None:
        tag_set_a = {'apple', 'banana', 'orange'}
        tag_set_b = {'apple', 'banana'}

        assert get_matching_b_percentage_from_tag_sets(tag_set_a, tag_set_b) == 1.0

    def test_partial_match(self) -> None:
        tag_set_a = {'apple'}
        tag_set_b = {'apple', 'banana', 'orange'}

        assert abs(get_matching_b_percentage_from_tag_sets(tag_set_a, tag_set_b) - 0.333) < 0.01


class TestSimplifyTagSet(TestCase):
    def test_no_hyphens(self) -> None:
        tag_set = {'apple', 'banana', 'orange'}

        result = simplify_tag_set(tag_set)

        assert result == {'apple', 'banana', 'orange'}

    def test_with_hyphens(self) -> None:
        tag_set = {'machine-learning', 'data-science'}

        result = simplify_tag_set(tag_set)

        assert 'machine' in result
        assert 'learning' in result
        assert 'data' in result
        assert 'science' in result


class TestSimplifyTagSetToList(TestCase):
    def test_mixed_tags(self) -> None:
        tag_set = {'apple', 'machine-learning'}

        result = simplify_tag_set_to_list(tag_set)

        assert 'apple' in result
        assert 'machine' in result
        assert 'learning' in result

    def test_with_hyphens(self) -> None:
        tag_set = {'machine-learning'}

        result = simplify_tag_set_to_list(tag_set)

        assert result == ['machine', 'learning']


class TestSimplifyAndWeightTagSetToDict(TestCase):
    def test_duplicate_words(self) -> None:
        tag_set = {'machine-learning', 'deep-learning'}

        result = simplify_and_weight_tag_set_to_dict(tag_set)

        assert result['learning'] == 2
        assert result['machine'] == 1
        assert result['deep'] == 1

    def test_simple_tags(self) -> None:
        tag_set = {'apple', 'banana'}

        result = simplify_and_weight_tag_set_to_dict(tag_set)

        assert result['apple'] == 1
        assert result['banana'] == 1

    def test_sorted_by_weight(self) -> None:
        tag_set = {'machine-learning', 'deep-learning', 'learning'}

        result = simplify_and_weight_tag_set_to_dict(tag_set)
        keys = list(result.keys())

        assert keys[0] == 'learning'
        assert result['learning'] == 3


class TestGetScorePercentageFromTagSetWeighted(TestCase):
    def test_empty_reference(self) -> None:
        tag_set_actual = {'apple', 'banana'}
        tag_set_reference = set()

        result = get_score_percentage_from_tag_set_weighted(tag_set_actual, tag_set_reference)

        assert result == 0.0

    def test_no_match(self) -> None:
        tag_set_actual = {'grape', 'kiwi'}
        tag_set_reference = {'apple', 'banana'}

        result = get_score_percentage_from_tag_set_weighted(tag_set_actual, tag_set_reference)

        assert result == 0.0

    def test_with_weighted_match(self) -> None:
        tag_set_actual = {'machine-learning', 'learning'}
        tag_set_reference = {'machine-learning', 'deep-learning'}

        result = get_score_percentage_from_tag_set_weighted(tag_set_actual, tag_set_reference)

        assert result > 0
