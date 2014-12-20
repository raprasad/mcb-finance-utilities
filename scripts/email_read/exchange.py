import imaplib, getpass
import os, sys

ST_OK = 'OK'

def check_hcom_mail(output_dir, retrieve_all_mail=False):
    """
    Retrieve unread HCOM email
    """
    if not os.path.isdir(output_dir):
        print 'Output director does not exist: %s' % output_dir
        sys.exit(0)
    
    print 'check_hcom_mail'
    # hostname = '2007exch.fasmail.harvard.edu'
    hostname = 'imap.fasmail.harvard.edu'
    username = 'fas_domain\user'
    passwd = getpass.getpass()
    print 'one'
    imap_conn = imaplib.IMAP4_SSL(host=hostname, port=993)
    print 'two'
    imap_conn.login(username, passwd)
    print 'three'

    status, mbox_list = imap_conn.list()
    if status == ST_OK:
        for mbox in mbox_list:
            print mbox
    
    print 'select HCOM mbox'
    status, messages = imap_conn.select('INBOX/mcb/HCOM_TEST_NEW')
    if status == ST_OK:
        
        if retrieve_all_mail:
            typ, data = imap_conn.search(None, 'ALL')   # pull all email
        else:
            typ, data = imap_conn.search(None, 'UnSeen') # pull unseen email 
        
        cnt = 0
        for num in data[0].split():
            cnt+=1
            typ_header, msg_id_data = imap_conn.fetch(num, '(BODY[HEADER.FIELDS (MESSAGE-ID)])')
            msg_id = msg_id_data[0][1].replace('Message-ID:', '').replace('<', '').replace('>', '').strip()
            
            #print 'Message %s\n%s\n' % (num, msg_data)
            print '(%s) message: %s' %  (cnt, msg_id)
            email_fname = os.path.join(output_dir, '%s.eml' % msg_id)
            if os.path.isfile(email_fname):
                print 'file exists'
                continue
            typ, data = imap_conn.fetch(num, '(RFC822)')
            msg_data = data[0][1]
            
            open(email_fname, 'w').write(msg_data)
            print 'file written', email_fname
            
    imap_conn.close()
    print 'closed'
    imap_conn.logout()
    print 'logged out'
    #return
    """
    imap_conn.select('Inbox')
    typ, data = imap_conn.search(None,'(UNSEEN SUBJECT "%s")' % subject)
    for num in data[0].split():
        typ, data = conn.fetch(num,'(RFC822)')
        msg = email.message_from_string(data[0][1])
        typ, data = conn.store(num,'-FLAGS','\\Seen')
        yield msg
    """
    
    
if __name__=='__main__':  
    print 'blah'   
    check_hcom_mail(output_dir='../data5', retrieve_all_mail=False)
    print 'blah'   
    