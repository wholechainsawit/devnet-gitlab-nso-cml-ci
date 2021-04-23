from virl2_client import ClientLibrary


def main():
    cml_id = "developer"
    cml_pw = "C1sco12345"
    cml_url = "https://10.10.20.161"
    lab_title = "TWO_CSR1kv"

    cml = ClientLibrary(cml_url, cml_id, cml_pw, allow_http=False, ssl_verify=False)
    if cml.find_labs_by_title(lab_title):
        lab_id = cml.find_labs_by_title(lab_title)[0].id
        lab = cml.join_existing_lab(lab_id)
        lab.stop()
        lab.wipe()
        lab.remove()
    else:
        print(f"Lab, {lab_title}, not found")


if __name__ == "__main__":
    main()
