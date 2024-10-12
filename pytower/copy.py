import json
from typing import Any, Mapping

from .object import TowerObject
from .selection import Selection
from .util import not_none
from .suitebro import get_active_save


def replace_guids(datadict: Mapping[str, Any] | None, replacement_table: dict[str, str]):
    encoding = json.dumps(datadict)
    for target, replacement in replacement_table.items():
        encoding = encoding.replace(target, replacement)
    return json.loads(encoding)


def fitem_guid(guid: str) -> str:
    return guid.replace('-', '').upper()


# Returns new selection containing the new copied objects
def copy_selection(selection: Selection) -> Selection:
    # First pass: new guids and setup replacement table
    replacement_table: dict[str, str] = {}
    copies: list[TowerObject] = [None] * len(selection)  # type: ignore
    new_groups: dict[int, int] = {}
    save_max_groupid = get_active_save().get_max_groupid()
    for x, obj in enumerate(selection):
        old_guid = None
        if obj.item is not None:
            old_guid = obj.item['guid']

        copied = obj.copy()

        old_group_id = obj.group_id
        if old_group_id >= 0:
            if old_group_id not in new_groups:
                max_new_groupid = max(new_groups.values()) if new_groups.values() else -1
                new_groupid = max(save_max_groupid, max_new_groupid) + 1
                new_groups[old_group_id] = new_groupid

            copied.set_group_id(new_groups[old_group_id])

        if old_guid is not None:
            new_guid = not_none(copied.item)['guid']
            replacement_table[old_guid] = new_guid

        copies[x] = copied

    full_replacement_table = {}
    for old, new in replacement_table.items():
        full_replacement_table[old] = new
        full_replacement_table[fitem_guid(old)] = fitem_guid(new)

    # Second pass: replace any references to old guids with new guids
    for obj in copies:
        obj.item = replace_guids(obj.item, full_replacement_table)
        obj.properties = replace_guids(obj.properties, full_replacement_table)

    return Selection(copies)
