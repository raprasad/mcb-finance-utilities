from lxml.html import clean 
import os
import re
from django.template.defaultfilters import removetags

class HCOMEmailCleaner:

    @staticmethod
    def pull_html_from_email_content(email_content):
        if email_content is None:
            return None
            
        idx = email_content.find('<html')
        if idx==-1:
            return None
        end_idx = email_content.find('</html>', idx+5)
        if end_idx==-1:
            return None

        html_content = email_content[idx:end_idx+7]

        # remove line breaks 
        strings_to_remove = ['=\r\n',  '<o:p>', '</o:p>']
        for to_remove in strings_to_remove:
            html_content = html_content.replace(to_remove, '')

        # remove <img ...> and <span...> tags
        html_content = removetags(html_content, 'p b img span')

        # remove extra attributes
        safe_attrs=clean.defs.safe_attrs
        clean.defs.safe_attrs=frozenset()
        cleaner = clean.Cleaner(safe_attrs_only=True)

        html_content = cleaner.clean_html(html_content)

        html_content = html_content.encode('ascii', 'ignore')
        return html_content          
        
    @staticmethod
    def pull_html_from_email_file(fname):
        if not os.path.isfile(fname):
            return None
            
        content = open(fname, 'r').read()
        return HCOMEmailCleaner.pull_html_from_email_content(content)
        
