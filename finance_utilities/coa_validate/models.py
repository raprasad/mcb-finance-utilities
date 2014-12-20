from django.db import models
from expense_code_definitions.ec_lookup import ExpenseCodeDefined, NOT_FOUND
#

        
class COADefinitionLoadLog(models.Model):
    coa_files_date = models.DateField()
    
    successful_file_copy = models.BooleanField(default=False)
    successful_database_load = models.BooleanField(default=False)

    file_copy_log = models.TextField(blank=True)
    file_load_log = models.TextField(blank=True)
    
    update_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return self.coa_files_date.strftime('%Y-%m-%d')

    class Meta:
        ordering = ('-coa_files_date', '-create_time', )
        verbose_name = 'COA File Load Log'
    
class CheckedExpenseCode(models.Model):
    """
    Record of expense codes that have already been checked
    """
    expense_code = models.CharField(max_length=33, db_index=True, unique=True, help_text='33-digit numeric code')
    is_valid = models.BooleanField(default=False)
    expense_code_formatted = models.CharField(max_length=39, db_index=True, help_text='auto-filled on save', blank=True)
    root_value = models.CharField(max_length=5, db_index=True, help_text='auto-filled on save', blank=True)
    update_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)

    def define_ec(self):
          if not len(self.expense_code)==33:
              return

          self.ec_defined = ExpenseCodeDefined.load_ec_str(self.expense_code)

    @staticmethod
    def format_expense_code_str(expense_code_str):
       
       if expense_code_str is None or not len(expense_code_str) == 33:
           return expense_code_str
           
       return '%s-%s-%s-%s-%s-%s-%s' % (expense_code_str[0:3]
                   , expense_code_str[3:8]
                   , expense_code_str[8:12]
                   , expense_code_str[12:18]
                   , expense_code_str[18:24]
                   , expense_code_str[24:28]
                   , expense_code_str[28:33]
                   )

    def save(self, *args, **kwargs):
        if self.expense_code and len(self.expense_code) >= 5:
            self.root_value = self.expense_code[-5:]
            
        self.expense_code_formatted = CheckedExpenseCode.format_expense_code_str(self.expense_code)
        super(CheckedExpenseCode, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.expense_code

    class Meta:
        ordering = ('root_value', 'expense_code_formatted',)
  