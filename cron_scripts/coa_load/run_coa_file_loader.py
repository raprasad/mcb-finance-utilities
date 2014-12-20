"""
Retrieve the COA definition files re: SCP and load them to the database

"""
import os, sys

sys.path.append('/var/webapps/django/mcb-finance-utilities/')
sys.path.append('/var/webapps/django/mcb-finance-utilities/finance_utilities')
sys.path.append('/Users/some-user/mcb-git/mcb-finance-utilities')
sys.path.append('/Users/some-user/mcb-git/mcb-finance-utilities/finance_utilities')

from finance_utilities import settings
from django.core.management import setup_environ
setup_environ(settings)

# pull in "BackupMaker"
sys.path.append('/var/webapps/django/mcb_lib/poor-mans-db-backup')
from expense_code_definitions.coa_file_retriever import CredFileReader, COAFileRetriever
from expense_code_definitions.defn_file_loader_sqlite import SqlLiteDefinitionFileLoader
from expense_code_definitions.defn_file_loader_mysql import MySqlDefinitionFileLoader

from coa_validate.models import COADefinitionLoadLog
#from backupdb.backup_files import BackupMaker


if __name__ == '__main__':
    creds = CredFileReader(settings.COA_CREDS_FILE)
    
    IS_LIVE_SERVER = True
    if not IS_LIVE_SERVER:
        retrieve_coa_kwargs = { 'scp_username' : creds.username\
                        , 'scp_password' : creds.pw\
                        , 'is_live_server' : IS_LIVE_SERVER\
                        , 'dest_dir' : '/Users/some-user/mcb-git/mcb-finance-utilities/cron_scripts/coa_load/'\
                    }    
    else:                        
        retrieve_coa_kwargs = { 'scp_username' : creds.username\
                        , 'scp_password' : creds.pw\
                        , 'is_live_server' : IS_LIVE_SERVER\
                        , 'dest_dir' : '/var/webapps/coa_files'\
                        }

    # STEP 1 - retrieve files
    cfr = COAFileRetriever(**retrieve_coa_kwargs)
    cfr.copy_yesterdays_backup()
    cfr.clear_old_coa_files()
    
    LOAD_LOG_OBJECT = COADefinitionLoadLog(coa_files_date=cfr.yesterday\
                            , successful_file_copy = cfr.load_success\
                            , file_copy_log=cfr.get_log_messages()\
                            )
    LOAD_LOG_OBJECT.save()
    
    # STEP 2 - load them to the db
    coa_file_dir = retrieve_coa_kwargs['dest_dir']
    coa_directory_names = filter(lambda x: os.path.isdir(os.path.join(coa_file_dir, x))\
                            , os.listdir(coa_file_dir))
    coa_directory_names = filter(lambda x: x.startswith(COAFileRetriever.COA_DIRECTORY_PREFIX)\
                            , coa_directory_names)
    coa_directory_names.sort()
    if len(coa_directory_names) > 0:
        segment_file_dir = os.path.join(coa_file_dir, coa_directory_names[-1])
        
        if IS_LIVE_SERVER:
            coa_loader = MySqlDefinitionFileLoader(segment_file_dir)    # MySQL
        else:
            coa_loader = SqlLiteDefinitionFileLoader(segment_file_dir)  # sqlite
        coa_loader.process_expense_code_files(clear_tables=True)
        # "False" flag, need a check for successful load
        LOAD_LOG_OBJECT.successful_database_load = True
        LOAD_LOG_OBJECT.save()
    
    
    
    
    
    
    
    