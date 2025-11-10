def get_matching_tag_set_from_tag_sets(tag_set_a: set[str], tag_set_b: set[str]) -> set[str]:
    return tag_set_a.intersection(tag_set_b)


def get_matching_count_from_tag_sets(tag_set_a: set[str], tag_set_b: set[str]) -> int:
    return len(get_matching_tag_set_from_tag_sets(tag_set_a, tag_set_b))


def get_matching_a_percentage_from_tag_sets(tag_set_a: set[str], tag_set_b: set[str]) -> float:
    try:
        return get_matching_count_from_tag_sets(tag_set_a, tag_set_b) / len(tag_set_a)
    except ZeroDivisionError:
        return 0.0


def get_matching_b_percentage_from_tag_sets(tag_set_a: set[str], tag_set_b: set[str]) -> float:
    try:
        return get_matching_count_from_tag_sets(tag_set_a, tag_set_b) / len(tag_set_b)
    except ZeroDivisionError:
        return 0.0
