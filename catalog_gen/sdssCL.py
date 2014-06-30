#!/usr/bin/env python

""">> sdssCL << command line query tool  copyleft (c) 2000-2001 by Tamas Budavari
Usage: sdssCL [options] sqlfile(s)                      [budavari@pha.jhu.edu]
Options:
        -u 			: get username from the environment
	-l <login_name>		: set username, otherwise you'll be prompted
        -p <port_daemon>	: format "host:port"
        -s <server_id>		: set server
        -a <ae_id>		: id of the analysis engine to lookup in PD
        -t <ae_host>		: analysis engine by "hostname:port"
        -q <query_string>	: command line query, process before file(s)
        -c			: don't launch queries, just return cost(s)
        -i			: print info message of the server (default no)
        -n			: no feedback on screen, quiet mode
        -d <delay>		: time delay in secs between status requests
        -g			: debug info on the network communication
        -V			: show version number
        -h or -?		: show this message"""

import os
import sys
import string
import time
import getopt
import getpass
import sdss

__version__ = '1.11'

def usage(status, msg=''):
    print __doc__
    if msg:
        print msg
    sys.exit(status)

#---------------------------------------------------------------------------

class clParam:
    """Command line parameters"""
    def __init__(self, argv):
        if len(argv)<1: usage(1)
        #--- defaults values
        self.portd = None
        self.server = None
        self.target = None
        self.ae = None
        self.username = None
        self.query = None
        self.debug = None
        self.justcost = None
        self.delay = 5
        self.info = sdss.false
        self.quiet = sdss.false
        self.timeout = 10
        #--- parse cmd line
        try:
            optlist, args = getopt.getopt(argv, 't:a:p:q:l:us:d:o:cingVh?')
        except getopt.error, msg:
            usage(1,'ERROR: '+msg)
        for o,a in optlist:
            if   o=='-t': self.target = a
            elif o=='-a': self.ae = a
            elif o=='-p': self.portd = a
            elif o=='-q': self.query = a
            elif o=='-l': self.username = a
            elif o=='-u': self.username = getpass.getuser() 
            elif o=='-s': self.server = a
            elif o=='-i': self.info = sdss.true
            elif o=='-g': self.debug = sdss.true
            elif o=='-n': self.quiet = sdss.true
            elif o=='-o': self.timeout = int(a)
            elif o=='-c': self.justcost = sdss.true
            elif o=='-d': self.delay = float(a)
            elif o=='-V':
                print '>> sdssCL << version', __version__
                sys.exit(0)
            else: usage(0)
        self.args = args
    
    def queries(self):
        ret = []
        if self.query:
            q = sdss.Query(self.query)
            q.filename = 'on the command line'
            ret.append(q)
        for file in self.args:
            q = sdss.Query()
            if file == '-':
                sys.stdout.write('# Type in your query - hit ^D to submit\n')
                sys.stdout.flush()
                q.parse(sys.stdin.read())
                q.filename = 'on stdin'
            else:
                q.load(file)
            ret.append(q)
        return ret


#---------------------------------------------------------------------------

def main(argv=sys.argv[1:]):

    """The main application to run queries"""
    if type(argv)==type(''):
        argv = string.split(argv)

    #--- parse cmd line and load all queries
    pmt = clParam(argv)
    qry = pmt.queries()
    if len(qry)<1: usage(1,'ERROR: No query!?!')

    if not pmt.portd: usage(1,'Specify port daemon')
    if not pmt.server: usage(1,'Specify server id')

    if not pmt.quiet:
        end = string.find(__doc__,"Usage")
        print __doc__[:end-1]

    #--- lookup the server in PD
    pdhost = sdss.Host(pmt.portd) 
    user   = sdss.User(pmt.username)

    pd = sdss.PortDaemon(pdhost, pmt.debug)
    pd.login(user)
    srhost = pd.lookup(pmt.server)
    pd.close()

    #--- lookup aengine if needed and store target in pmt
    if pmt.ae and not pmt.justcost:
        pd.reconnect()
        try:
            aehost = pd.lookup(pmt.ae)
            pd.close()
            pmt.target = str(aehost)
        except sdss.error, msg:
            sdss.perror(msg)

    #--- lookup aengines of queries or set file if just cost estimate
    for i in range(len(qry)):
        #--- first qry has different priority
        if i==0 and pmt.target:
            qry[i].target = 'SOCKET '+str(pmt.target)
        #--- no target but cost or ae or pmt -> set
        if pmt.justcost:
            qry[i].target = 'FILE /tmp/cost.sdssCL'
        if not qry[i].target:
            if qry[i].aengine:
                pd.reconnect()
                t = pd.lookup(qry[i].aengine)
                qry[i].target = 'SOCKET '+str(t)
            elif pmt.target:
                qry[i].target = 'SOCKET '+str(pmt.target)
            
    #--- login to server
    sr = sdss.Server(srhost, pmt.debug, bufsize=2048)
    sr.timeout = pmt.timeout
    sr.login(user)

    #--- get version from server and also info msg
    try:
        ver =  string.replace(sr.version(),'_','.')
    except sdss.error:
        ver = 'unknown version'
    if not pmt.quiet:
        print "## Connected to %s %s" % (pmt.server,ver)
        if pmt.info:
            print sr.info()
    
    #--- launch all queries and get status
    if 1:
        done = 0
        for i in range(len(qry)):
            sr.submit(qry[i])
            sr.launch(qry[i])
            if not pmt.quiet:
                print '**', 'Cost analysis for query', qry[i].filename
                print ' ' + qry[i].cost
            if pmt.justcost:
                sr.abort(qry[i])
                qry[i].done = sdss.true
                done = done+1
            
        #--- check status of all, abort them if ^C
        try:
            while done<len(qry):
                done = 0
                time.sleep(pmt.delay)
                for i in range(len(qry)):
                    if not qry[i].done:
                        sr.status(qry[i])
                        if not pmt.quiet:
                            sys.stdout.write(str(qry[i])+'\n')
                    if qry[i].done: done = done+1
        except KeyboardInterrupt:
            for i in range(len(qry)):
                if not qry[i].done:
                    sr.abort(qry[i])

    sr.close()
    return 0

#---------------------------------------------------------------------------

# Just do it...
if __name__=='__main__':
    try:
        stat = main()
        sys.exit(stat)
    except sdss.error, msg:
        sdss.perror(msg)
    except sdss.timeout, msg:
        sdss.perror(msg)


