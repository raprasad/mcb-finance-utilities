import sys

def msg(s): print s
def dashes(): msg(40*'-')
def msgt(s): dashes(); msg(s); dashes()
def msgx(s): dashes(); msg(s); dashes(); msg('Exiting'); sys.exit(0)

