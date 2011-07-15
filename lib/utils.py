import os
import json

#Utils

#File Load/Store
def read_file(infile):
    with open(infile, 'r') as f:
        data = ''.join(f.readlines())
    f.close()
    return data

def write_file(outfile, data):
    with open(outfile, 'w') as f:
        f.writelines([data])
    f.close()
    return

#JSON Load/Store
def load_status(infile):
    data = '{}'
    if os.access(infile, os.R_OK):
        data = read_file(infile)

    return json.loads(data)

def store_status(outfile, obj):
    write_file(outfile, json.dumps(obj))
    return

def check_epoch(obj, passname):
    pass

def sign_epoch(obj, passname):
    pass

#test case
if __name__ == '__main__':
    obj = load_status('/tmp/test.status')
    print(obj)
    store_status('/tmp/test.status', obj)
