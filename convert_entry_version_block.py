import argparse
import sys

from django.core.wsgi import get_wsgi_application
from django.db.models import QuerySet

app = get_wsgi_application()

from django_spire.knowledge.entry.version.block.blocks.block import BaseBlock
from django_spire.knowledge.entry.version.block.entities import HeadingEditorBlockData, \
    BaseEditorBlockData, ListEditorBlockData, ListItemEditorBlockData, \
    ListEditorBlockDataStyle, TextEditorBlockData
from django_spire.knowledge.entry.version.block.choices import BlockTypeChoices
from django_spire.knowledge.entry.version.block.models import EntryVersionBlock
from django_spire.knowledge.entry.version.models import EntryVersion


class EntryVersionEditorJSDataMigrator:
    def __init__(
        self,
        dry_run: bool = False,
        target_entries: QuerySet[EntryVersion] = None,
    ) -> None:
        entry_versions = target_entries or EntryVersion.objects.all()

        self.dry_run = dry_run
        self._entry_block_queue = []
        self._old_list_items = []
        self._entry_versions = entry_versions.prefetch_related('blocks').all()
        self._current_processing_entry_version = None
        self._current_processing_entry_version_block = None

    @staticmethod
    def _convert_old_base_block_to_editor_block_data(old_block: BaseBlock) -> BaseEditorBlockData | None:
        match old_block.type:
            case BlockTypeChoices.TEXT:
                return TextEditorBlockData(
                    text=old_block.value,
                )
            case BlockTypeChoices.HEADING:
                return HeadingEditorBlockData(
                    text=old_block.value,
                    level=1,
                )
            case BlockTypeChoices.SUB_HEADING:
                return HeadingEditorBlockData(
                    text=old_block.value,
                    level=3,
                )
            case _:
                raise Exception(f'Unhandled block type: {old_block.type}')

    def _combine_list_block_items_into_new_entry_version_block(self) -> EntryVersionBlock:
        """
        Convert a flat list of ListItemBlock objects into a nested ListEditorBlockData structure.
        """
        style = ListEditorBlockDataStyle.ORDERED if self._old_list_items[
            0].ordered else ListEditorBlockDataStyle.UNORDERED

        stack = [(0, [])]

        for item in self._old_list_items:
            current_indent = item.indent_level

            while len(stack) > 1 and stack[-1][0] >= current_indent:
                stack.pop()

            new_item = ListItemEditorBlockData(
                content=item.value,
                meta=None,
                items=[],
                ordered=item.ordered
            )

            stack[-1][1].append(new_item)

            stack.append((current_indent, new_item.items))

        self._old_list_items = []

        editor_block_data = ListEditorBlockData(
            style=style,
            meta=None,
            items=stack[0][1]
        )

        new_entry_block = EntryVersionBlock(
            entry_version=self._current_processing_entry_version,
            editor_id=self._current_processing_entry_version_block.pk,
            type=BlockTypeChoices.LIST,
        )
        new_entry_block.editor_block_data = editor_block_data

        return new_entry_block

    def _add_entry_version_block_to_queue(self, entry_version_block: EntryVersionBlock) -> None:
        entry_version_block.order = len(self._entry_block_queue)
        self._entry_block_queue.append(entry_version_block)

    def _migrate_entry_version_block_to_editor_block_data(self, entry_version_block: EntryVersionBlock) -> None:
        old_block = entry_version_block.editor_block_data

        if old_block.type == BlockTypeChoices.LIST_ITEM:
            self._old_list_items.append(old_block)
            return

        if len(self._old_list_items) > 0:
            new_list_entry_version_block = self._combine_list_block_items_into_new_entry_version_block()
            self._add_entry_version_block_to_queue(new_list_entry_version_block)

        new_editor_block_data = self._convert_old_base_block_to_editor_block_data(old_block)
        entry_version_block.editor_block_data = new_editor_block_data

        self._add_entry_version_block_to_queue(entry_version_block)

    def _delete_old_entry_version_block_list_items(self) -> None:
        # Purge old list item blocks from the database
        old_entry_version_block_list_items = EntryVersion.objects.filter(
            type=BlockTypeChoices.LIST_ITEM)

        num_old_list_item_blocks = old_entry_version_block_list_items.count()

        if self.dry_run:
            print(
                f'Dry run: Would have purged {old_entry_version_block_list_items} list item blocks')
        else:
            print(
                f'Purging {num_old_list_item_blocks} list item blocks')
            old_entry_version_block_list_items.delete()

    def _save_queued_entry_version_block_changes(self) -> None:
        for entry_block in self._entry_block_queue:
            if self.dry_run:
                print(f'Dry run: Would have saved entry block {entry_block}')
            else:
                print(f'Saving entry block {entry_block}')
                entry_block.save()


    def migrate_entry_version_blocks_to_editor_block_data(self) -> None:
        for entry in self._entry_versions:
            self._current_processing_entry_version = entry

            for entry_block in entry.blocks.all():
                self._migrate_entry_version_block_to_editor_block_data(entry_block)

        self._delete_old_entry_version_block_list_items()
        self._save_queued_entry_version_block_changes()



if __name__ == '__main__':
    commit = False
    parser = argparse.ArgumentParser(
        description='Migrate entry version blocks to editor block data.')
    parser.add_argument('--commit', action='store_true',
                        help='Commit changes to the database')
    parser.add_argument('--target-entry')
    args = parser.parse_args()

    if args.commit:
        print(
            'WARNING - Changes will be committed to the database. Are you sure you want to continue? (y/n)')
        user_input = input()
        if user_input.lower() == 'y':
            commit = True
        else:
            print('Aborting migration')
            sys.exit(0)
    else:
        commit = False

    if args.target_entry:
        target_entries = EntryVersion.objects.filter(
            entry__id=args.target_entry)
    else:
        target_entries = None

    EntryVersionEditorJSDataMigrator(
        dry_run=not commit,
        target_entries=target_entries,
    ).migrate_entry_version_blocks_to_editor_block_data()