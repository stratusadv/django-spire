from __future__ import annotations

from django.template.loader import get_template
from django.template.loader_tags import ExtendsNode


def template_extends(template_name: str, ancestor_names: frozenset[str]) -> bool:
    """
    Whether ``template_name`` is one of ``ancestor_names`` or reaches one
    through its chain of literal ``{% extends %}`` tags.
    """
    visited: set[str] = set()

    while template_name not in visited:
        if template_name in ancestor_names:
            return True

        visited.add(template_name)
        extends_nodes = get_template(template_name).template.nodelist.get_nodes_by_type(ExtendsNode)

        if not extends_nodes or not isinstance(extends_nodes[0].parent_name.var, str):
            return False

        template_name = extends_nodes[0].parent_name.var

    return False
