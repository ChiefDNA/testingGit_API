data_store = {}


def get_data():
    return data_store


def get_data_by_id(id):
    return data_store.get(id)


def create_data(data):
    new_id = max(data_store.keys()) +1 if data_store else 1
    data_store[new_id] = data
    return new_id


def update_data(id, data):
    if id in data_store:
        data_store[id] = data
        return True
    return False


def delete_data(id):
    if id in data_store:
        del data_store[id]
        return True
    return False