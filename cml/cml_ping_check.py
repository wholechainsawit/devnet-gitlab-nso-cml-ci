import socket
import os
import time
import argparse
from concurrent.futures import ThreadPoolExecutor
from virl2_client import ClientLibrary


def ping_and_ssh_check(dev):
    cml_id = "developer"
    cml_pw = "C1sco12345"
    cml_url = "https://10.10.20.161"
    lab_title = "TWO_CSR1kv"
    cml = ClientLibrary(cml_url, cml_id, cml_pw, allow_http=False, ssl_verify=False)
    lab_id = cml.find_labs_by_title(lab_title)[0].id
    lab = cml.join_existing_lab(lab_id)

    node = lab.get_node_by_label(dev["name"])

    # wait for the node to be in the BOOTED state
    waited = 0
    while not node.is_booted():
        time.sleep(10)
        waited += 10
        print(f"{dev['name']}: Waited for {waited} sec...")
    print(f"{dev['name']}: is in BOOTED state")

    num_ping = 0
    # ping ip to see if the device is really up
    while os.system("ping -c 1 {} > /dev/null".format(dev["ip"])):
        time.sleep(10)
        num_ping += 1
        print(f"{dev['name']}: ping {num_ping}...")
    msg = f"{dev['name']} responded ping"

    for i in range(10):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        try:
            s.connect((dev["ip"], 22))
            s.shutdown(socket.SHUT_RDWR)
            print(f"SSH of device, {dev['name']} {dev['ip']}, is UP")
            break
        except:
            print(f"Tried #{i}: SSH of device, {dev['name']}, not up yet")
        finally:
            s.close()
        # hold the horse for 5 seconds before next try
        time.sleep(5)

    return msg


def run_multithread_loading(devs):
    futures_list = []
    results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        for dev in devs:
            future = executor.submit(ping_and_ssh_check, dev)
            futures_list.append(future)

        for future in futures_list:
            try:
                # result = future.result()
                result = future.result(timeout=600)
                results.append(result)
            except Exception:
                results.append(None)
        return results


def main():
    devs = [
        {"name": "csr1000v-0", "ip": "10.10.20.56"},
        {"name": "csr1000v-1", "ip": "10.10.20.57"},
    ]
    results = run_multithread_loading(devs)
    for result in results:
        print(result)


if __name__ == "__main__":
    main()
