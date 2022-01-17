def read():
    latest_block = None

    try:
        with open("latest_parsed_block") as f:
            latest_block = f.readline()
    except FileNotFoundError:
        print('File with latest parsed block not found, will create')

    if latest_block:
        return int(latest_block)

    return False


def write(block):
    with open("latest_parsed_block", "w+") as f:
        return f.write(str(block))
