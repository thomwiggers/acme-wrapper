#!/bin/python3
import sys
import os.path

# Very ugly script

domains = sys.argv[1:]

path = os.path.abspath(os.path.dirname(__file__))
confpath = '/etc/letsencrypt-certs'
acmepath = '/var/www/letsencrypt'

if len(domains) < 1:
    print("echo You need to specify the domains!")
    sys.exit()

print("set -e")
print("mkdir -p {}".format(os.path.join(confpath, domains[0])))
print("chmod 700 {}".format(os.path.join(confpath, domains[0])))
print("openssl ecparam -genkey -name secp384r1 -out {}".format(
    os.path.join(confpath, domains[0], 'private.key')))

if len(domains) == 1:
    print('openssl req -new -sha256 -key {0}/{1}/private.key'
          ' -subj "/CN={1}" -out {0}/{1}/request.csr'.format(
            confpath, domains[0]))
else:
    req = (
        r'openssl req -new -sha256 -key {2}/{0}/private.key '
        r'-subj "/" -reqexts SAN -config '
        r'<(cat /etc/ssl/openssl.cnf <(printf "[SAN]\nsubjectAltName={1}")) '
        r'-out {2}/{0}/request.csr'
    ).format(domains[0],
             ','.join(['DNS:{}'.format(x) for x in domains]),
             confpath)
    print(req)

print(("python {1}/acme-tiny/acme_tiny.py "
       "--account-key {1}/account.key "
       "--csr {2}/{0}/request.csr "
       "--acme-dir {3} "
       "> {2}/{0}/certificate.crt"
       ).format(domains[0], path, confpath, acmepath))
print(("[ -f {0}/intermediate.pem ] || "
       "wget https://letsencrypt.org/certs/lets-encrypt-x3-cross-signed.pem "
       "-O {0}/intermediate.pem").format(confpath))
print(("cat {1}/{0}/certificate.crt "
       "{1}/intermediate.pem "
       "> /etc/letsencrypt-certs/{0}/chained.pem").format(domains[0], confpath))
print(("(crontab -l; echo '0 0 1,11,21 * * /root/acme-tiny/renew.sh {0} 2>> "
       "{1}/acme-tiny.log') | crontab").format(domains[0], path))

# vim: set et sw=4 ts=4 :
