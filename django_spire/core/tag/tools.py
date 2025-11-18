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


def get_score_percentage_from_tag_set_weighted(tag_set_actual: set[str], tag_set_reference: set[str]) -> float:
    total_points = len(simplify_tag_set(tag_set_reference))

    multiplier = get_matching_count_from_tag_sets(tag_set_actual, tag_set_reference)

    weighted_points = sum(
        weight
        for tag, weight in simplify_and_weight_tag_set_to_dict(tag_set_reference).items()
        if tag in tag_set_actual
    )

    if weighted_points == 0 or total_points == 0:
        return 0.0

    return (weighted_points / total_points) * multiplier


def simplify_tag_set(tag_set: set[str]) -> set[str]:
    return set(simplify_tag_set_to_list(tag_set))


def simplify_tag_set_to_list(tag_set: set[str]) -> list[str]:
    simplified_tag_words = []

    for tag in tag_set:
        tag_words = tag.split('-')
        simplified_tag_words.extend(tag_words)

    return simplified_tag_words


def simplify_and_weight_tag_set_to_dict(tag_set: set[str]) -> dict[str, int]:
    simplified_and_weighted_tag_words = {}

    for tag_word in simplify_tag_set_to_list(tag_set):
        simplified_and_weighted_tag_words[tag_word] = simplified_and_weighted_tag_words.get(tag_word, 0) + 1

    return dict(
        sorted(
            simplified_and_weighted_tag_words.items(),
            key=lambda item: item[1],
            reverse=True
        )
    )
