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
    return json.loads(read_file(infile))

def store_status(outfile, obj):
    write_file(outfile, json.dumps(obj))
    return
