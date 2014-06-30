"""Science Archive Python API   copyleft (c) 2000-2001 by Tamas Budavari"""

# Exceptions
error = 'sdss.error'
timeout = 'sdss.timeout'

# Constants
false = 0
true  = 1

# Common modules
import os
import sys
import string
import socket
import signal

# Check if windoze
win = false
if sys.platform=='win32': win = true
    
# Classes
class Host:
    """Host class"""

    def __init__(self, host):
        if type(host)==type(''):
            tokens = string.split(host,':')
            self.name = tokens[0]
            self.port = int(tokens[1])
        else:
            self.name = host[0]
            self.port = host[1]
        
    def __str__(self):
        return '%s:%s' % (self.name, str(self.port))

    def __repr__(self):
        return 'Host at "%s"' % str(self)


class User:
    """User class"""

    def __init__(self, name=None, ofp=sys.stdout, passwd=None):
        thetruth = 'AndyIsGreat' # ask Gyula Szokoly ;-)
        prompt = 'Username: '

        try:
            self.fn = os.path.join(os.environ['HOME'],'.sdssCLau')
        except KeyError:
            self.fn = ''

        self.passwd = passwd
        
        if name:
            self.name = name
        else:
            try:
                self.load()
            except:
                ofp.write(prompt)
                self.name = raw_input()
            
        if not self.passwd:
            if name:
                ofp.write(prompt+self.name+'\n')
            import getpass
            ofp.write('Password: ')
            code = getpass.getpass('')
            if ofp==sys.stderr: ofp.write('\n')
            self.passwd = md5hex(code+thetruth)
        
    def __str__(self):
        return self.name

    def load(self, fname=None):
        import zlib
        if not fname: fname = self.fn
        ifp = open(fname,'rb')
        b = ifp.read()
        c = zlib.decompress(b)
        self.passwd = c[:16]+c[-16:]
        self.name = c[16:-16]
        
    def save(self, fname=None):
        try:
            import zlib
        except ImportError:
            sys.stderr.write("User cannot be saved: missing zlib?\n")
            return
        if not fname: fname = self.fn
        s = self.passwd[:16]+self.name+self.passwd[16:]
        c = zlib.compress(s)
        open(fname,'wb').write(c)
        os.chmod(fname,384) # permissions - r-- --- ---


def timeout_handler(signum, frame):
    """Signal handler raise exception sdss.timeout"""
    raise timeout, 'server hangs?'
#--- register handler
if not win: signal.signal(signal.SIGALRM, timeout_handler)


class Connect:
    """Base class for connecting to servers"""

    def __init__(self, server, debug, bufsize):
        if type(server)==type(''):
            server = Host(server)
        self.server = server
        self.debug = debug
        self.bufsize = bufsize
        self.user = None
        self.timeout = 20
        self.connect()
        
    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.socket.connect((self.server.name, self.server.port))
        except socket.error, msg:
            raise error, msg

    def send(self, arg):
        self.socket.send(arg+'\n')
        if self.debug:
            print 'SENT:', arg

    def recv(self):
        if not win: signal.alarm(self.timeout)		#-- set timer alarm
        ret = self.socket.recv(self.bufsize)
        if not win: signal.alarm(0)			#-- disable alarm
        if self.debug: print 'RECV:', ret[:-1]
        if not ret and isinstance(self,Server):
            raise error, '[recv] Empty line received!'
        return ret[:-1]

    def recvtok(self):
        data = self.recv()
        tokens = string.split(data)
        if type(tokens) != type([]) or type(tokens[0]) != type(''):
            raise error, '[recvtok] Wrong tokens!'
        return tokens

    def login(self, user=None):
        if user:
            self.user = user
        self.send('USER %s' % self.user.name)
        tokens = self.recvtok()
        if tokens[0] != 'ACK':
            raise error, '[login] Unknown user!'
        self.send('OK')
        tokens = self.recvtok()
        if tokens[0] != 'CHAL':
            raise error, '[login] No challange string received!'
        chal = tokens[1]
        userReply= md5hex("%s %s" % (chal,self.user.passwd))
        checkReply = md5hex(userReply)
        self.send('RESP %s %s' % (userReply,checkReply))
        tokens = self.recvtok()
        if tokens[0] != 'ACK':
            raise error, '[login] Invalid passwd!'
        
    def close(self):
        self.socket.close()

    def __str__(self):
        return str(self.server)

    def __repr__(self):
        return 'Connection to "%s"' % str(self)

class PortDaemon(Connect):
    """API for the port daemons"""

    def __init__(self, server=None, debug=None, bufsize=1024):
        Connect.__init__(self, server, debug, bufsize)        
    
    def register(self, id, host, permanent=false):
        msg = 'REGISTER %s %s %d ' % (id, host.name, host.port)
        if permanent:
            msg = msg+'PERMANENT' 
        else:
            msg = msg+'TRANSIENT' 
        self.send(msg)
        tokens = self.recvtok()
        if tokens[0] == 'REGISTER':
            ret = 1
        elif tokens[0] == 'WARNING':
            ret = 2
        else:
            raise error, '[register] Cannot register!'
        return ret

    def lookup(self, id):
        self.send('LOOKUP '+id)
        tokens = self.recvtok()
        if tokens[0] == 'LOOKUP':
            return Host(tokens[2]+':'+tokens[3])
        else:
            raise error, '[lookup] '+string.join(tokens[1:])

    def remove(self, id):
        self.send('REMOVE '+id)
        tokens = self.recvtok()
        if tokens[0] != 'REMOVE':
            raise error, '[remove] Cannot remove!'
        
    def dump(self):
        self.send('DUMP');
        ret = []
        while 1:
            line = self.recv()
            tok = string.split(line)
            if len(tok)>0 and tok[0]=='ERROR':
                raise error, '[dump] '+string.join(tok[1:])
            if not line: break
            ret.append(line)
        return string.join(ret,'\n')
        
    def reconnect(self):
        self.connect()
        self.login()

class Query:
    """Class holds query related..."""
    def __init__(self, qstr=None):
        self.id = None
        self.cost = None
        self.status = ''
        self.sxql = []
        self.target = None
        self.aengine = None
        self.mode = 'ASCII'
        self.filename = None
        self.done = false
        if qstr: self.parse(qstr)

    def load(self, fname):
        self.filename = fname
        self.parse(open(fname).read())

    def parse(self, qstr):
        "Parse query string and store info"
        if type(qstr) != type(''):
            raise error, '[parse] Query is not a string!'
        lines = string.split(qstr,'\n')
        for line in lines:
            # find target or ae if present
            tok = string.split(line)
            if len(tok)>0:
                keyw = string.lower(tok[0])
                if   keyw == '#target':
                    self.target = 'SOCKET '+tok[1]
                    if string.lower(tok[2])=='binary': self.mode = 'Binary'
                elif keyw == '#aengine':
                    self.aengine = tok[1]
                    if string.lower(tok[2])=='binary': self.mode = 'Binary'
                elif keyw in ['#proxlist', '#matchlist']:
                    raise error, '[parse] Does NOT support proxlist'
            # get rid of comments
            end = len(line)+1
            for comment in ['//','#','--']:
                e = string.find(line,comment)
                if e != -1 and e < end: end = e
            line = line[:end]
            # insert line     
            self.sxql.append(line)
    
    def __str__(self):
        path, name = os.path.split(self.filename)
        status = self.status[0][:1]
        status = status + " %3s%%  %8s" % (self.status[2],self.status[3])
        s = " [%s]  %s   %s" % (self.id, name, status)
        return string.ljust(s,40
                            )
class Server(Connect):
    """API for the servers"""

    def __init__(self, server, debug=None, bufsize=1024):
        Connect.__init__(self, server, debug, bufsize)
        
    def version(self):
        self.send('VERSION')
        tok = self.recvtok()
        while tok[0] != 'VERSION':
            tok = self.recvtok()
        if tok[1] == '0': tok[1]=''
        return string.strip(string.join(tok[1:]))

    def info(self, tab='   - '):
        self.send('INFO')
        tok = self.recvtok()
        while tok[0] != 'INFO' and tok[0] != 'ERROR':            
            tok = self.recvtok()
        if tok[0] == 'ERROR':
            raise error, '[info] '+string.join(tok[1:])            
        ret = tab + string.join(tok[2:7]) + '\n'
        ret = ret + tab + string.join(tok[7:16]) +'\n'
        ret = ret + tab + string.join(tok[16:])
        return ret

    def submit(self, qry):
        self.send('BEGIN QUERY '+str(qry.mode)+' '+str(qry.target))
        for line in qry.sxql: self.send(line)
        self.send(';')
        self.send('END QUERY')
        # get first
        data = self.recv()
        tok = string.split(data)
        if tok[0] == 'ERROR':
            raise error, '[query] '+string.join(tok[1:])
        # repeat if not BC
        while tok[0] != 'BC':
            data = self.recv()
            tok = string.split(data)
            if tok[0] == 'ERROR':
                raise error, '[query] '+string.join(tok[1:])
        start = string.find(data,'#')
        end = string.rfind(data,'"')
        qry.id = tok[1]
        qry.cost = data[start:end+1]

    def status(self, qry):
        self.send('STATUS %s' % qry.id)
        tok = self.recvtok()
        while tok[1] != qry.id: tok = self.recvtok()
        nerror = int(tok[3])
        if nerror==0:
            qry.status = tok[2:]
        else:
            errors = ''
            for i in range(nerror):
                errors = errors +self.recv() +' '
            raise error, '[status] ' +errors
        if qry.status[0] == 'IDLE' and qry.status[2] == '100':
            qry.done = true
            
    def launch(self, qry):
        self.send('START %s' % qry.id)
        
    def abort(self, qry):
        self.send('ABORT %s' % qry.id)
        self.status(qry)
        while qry.status[0] != 'IDLE':
            self.status(qry)
        
    def suspend(self, qry):
        self.send('SUSPEND %s' % qry.id)

    def resume(self, qry):
        self.send('RESUME %s' % qry.id)

    def close(self):
        self.send('EXIT')
        tok = self.recvtok()
        while tok[0]=='STATUS':
            tok = self.recvtok()
        if tok[0] != 'END':
            raise error, '[close] '+string.join(tok)
        self.socket.close()

        
# Util functions
def md5hex(arg):
    """md5 wrapper"""
    import md5
    s = md5.new(arg).digest()
    return "%02x"*len(s) % tuple(map(ord,s))


def perror(arg='No message...', status=1, ofp=sys.stderr, exit=true):
    """error message and exit"""
    from types import *
    if type(arg)==TupleType or type(arg)==ListType:
        msg = ''
        for w in arg: msg = msg +str(w) +' '
    elif type(arg)==StringType:
        msg = arg
    else:
        msg = str(arg)
    ofp.write('SDSS ERROR: '+msg+'\n')
    if exit:
        sys.exit(status)


# print documentation string if executed
if __name__=='__main__': print __doc__
