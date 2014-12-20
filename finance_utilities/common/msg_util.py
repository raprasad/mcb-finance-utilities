import os, sys, string

def msg(s):
    print s
    
def dashes():
    msg(40*'-')

def msgt(s):
    dashes()
    msg(s)
    dashes()

def msgu(s):
    dashes()
    msg(s)
    
def msgx(s):
    msgt('Error')
    msg(s)
    dashes()
    sys.exit(0)
    