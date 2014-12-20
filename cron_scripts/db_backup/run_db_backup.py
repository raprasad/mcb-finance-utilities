import os, sys

sys.path.append('/var/webapps/django/mcb-finance-utilities/')
sys.path.append('/var/webapps/django/mcb-finance-utilities/finance_utilities')

from finance_utilities import settings
from django.core.management import setup_environ
setup_environ(settings)

# pull in "BackupMaker"
sys.path.append('/var/webapps/django/mcb_lib/poor-mans-db-backup')
from backupdb.backup_files import BackupMaker


if __name__ == '__main__':
    mb = BackupMaker(backup_name='Finance Utilities (hcom training)')
    mb.make_backup()

