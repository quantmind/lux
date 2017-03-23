from lux.core import LuxCommand, option
from ..migrations import migrations


class Command(LuxCommand):
    help = 'Alembic commands for migrating database'

    def command_init(self):
        """Initialise alembic migration directory
        """
        migrations(self.app).init()

    @option('-m', '--message', help='Revision message')
    @option('--branch-label',
            help='Specify a branch label to apply to the new revision')
    def command_migrate(self, message, branch_label):
        """Autogenerate a new revision file

        alias for 'revision --autogenerate'
        """
        migrations(self.app).upgrade(message, autogenerate=True,
                                     branch_label=branch_label)

    @option('--autogenerate', action='store_true', default=False,
            help=('Populate revision script with candidate migration '
                  'operations, based on comparison of database to model'))
    @option('-m', '--message', help='Revision message')
    @option('--branch-label',
            help='Specify a branch label to apply to the new revision')
    def command_revision(self, autogenerate, message, branch_label):
        """Create a new revision file
        """
        migrations(self.app).revision(message, autogenerate=autogenerate,
                                      branch_label=branch_label)

    @option('revision', default='heads')
    def command_upgrade(self, target):
        """Run upgrade migrations
        """
        migrations(self.app).upgrade(target)

    @option('revision', default='1')
    def command_downgrade(self, target):
        """Run upgrade migrations
        """
        migrations(self.app).downgrade(target)

    @option('revision', default='heads', help='revision to show')
    def command_show(self, revision):
        """Show the given revision"""
        migrations(self.app).show(revision)

    @option('revision', default='heads', help='revision to stamp')
    def command_stamp(self, revision):
        """stamp the revision table with the given revision

        don't run any migrations
        """
        migrations(self.app).stamp(revision)

    @option('-m', '--message', help='Merge revision message')
    @option('--branch-label',
            help='Specify a branch label to apply to the new revision')
    @option('--rev-id',
            help='Specify a hardcoded revision id instead of generating one')
    @option('revisions', nargs=2,
            help='The two revisions to merge')
    def command_merge(self, message, branch_label, rev_id, revisions):
        """Merge two revisions together, creating a new revision file
        """
        migrations(self.app).merge(message, branch_label=branch_label,
                                   rev_id=rev_id, revisions=revisions)
