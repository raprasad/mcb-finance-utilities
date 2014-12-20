from django.contrib import admin
from coa_validate.models import CheckedExpenseCode, COADefinitionLoadLog
from coa_validate.forms_admin import CheckedExpenseCodeForm

class COADefinitionLoadLogAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('file_copy_log', 'file_load_log',  )
    list_filter = ('successful_file_copy', 'successful_database_load', )    
    readonly_fields = ('update_time', 'create_time',)
    list_display = ('coa_files_date',  'successful_file_copy', 'successful_database_load', 'create_time'  )
admin.site.register(COADefinitionLoadLog, COADefinitionLoadLogAdmin)


class CheckedExpenseCodeAdmin(admin.ModelAdmin):
    save_on_top = True
    form = CheckedExpenseCodeForm
    search_fields = ('expense_code_formatted', 'expense_code', 'root_value', )
    list_filter = ('root_value',)    
    readonly_fields = ('expense_code_formatted', 'root_value',)
    list_display = ('expense_code_formatted',  'root_value', 'update_time', 'create_time' )
admin.site.register(CheckedExpenseCode, CheckedExpenseCodeAdmin)

