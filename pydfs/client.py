import os
import sys
import rpyc

def send_to_minion(block_uuid, data, minions):
    print("sending: " + str(block_uuid) + str(minions))
    main_minion, *replicate_minions = minions
    host, port = main_minion

    con = rpyc.connect(host, port=port)
    minion = con.root.Minion()
    minion.put(block_uuid, data, replicate_minions)

def read_from_minion(block_uuid, minion):
    host, port = minion
    con = rpyc.connect(host, port=port)
    minion = con.root.Minion()
    return minion.get(block_uuid)

def delete_from_minion(block_uuid, minion):
    host, port = minion
    con = rpyc.connect(host, port=port)
    minion = con.root.Minion()
    return minion.delete(block_uuid)

def get(master, fname):
    file_table = master.read(fname)
    if not file_table:
        print("404: file not found")
        return

    for block_uuid, nodes_ids in file_table:
        for m in [master.get_minions()[_] for _ in nodes_ids]:
            data = read_from_minion(block_uuid, m)
            if data:
                sys.stdout.write(data)
                break
            else:
                print("No blocks found. Possibly a corrupt file")

def put(master, source, dest):
    size = os.path.getsize(source)
    blocks = master.write(dest, size)
    with open(source) as f:
        for block_uuid, node_ids in blocks:
            data = f.read(master.get_block_size())
            minions = [master.get_minions()[_] for _ in node_ids]
            send_to_minion(block_uuid, data, minions)

def delete(master, fname):
    file_table = master.read(fname)
    if not file_table:
        print("404: file not found")
        return

    master.delete(fname)
    for block_uuid, node_ids in file_table:
        for m in [master.get_minions()[_] for _ in node_ids]:
            delete_from_minion(block_uuid, m)

def backup(master, mid):
    master.replicate(int(mid))


def main(args):
    con = rpyc.connect('localhost', 2130)
    proxy = con.root.Proxy()
    master = proxy.get_master()

    if args[0] == "get":
        get(master, args[1])
    elif args[0] == "put":
        put(master, args[1], args[2])
    elif args[0] == "delete":
        delete(master, args[1])
    elif args[0] == "backup":
        backup(master, args[1])
    else:
        print("try 'put srcFile destFile OR get file'")


if __name__ == "__main__":
    main(sys.argv[1:])
