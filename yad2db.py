from tinydb import TinyDB, Query, where
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import JSONStorage

class Yad2DB(object):
    """docstring for Yad2DB"""
    def __init__(self, uid):
        super(Yad2DB, self).__init__()
        db_path = f"db/{uid}"
        self.db_path = db_path

    def __enter__(self):
        self.db = TinyDB(self.db_path, storage=CachingMiddleware(JSONStorage))
        return self

    def __exit__(self, type, value, traceback):
        self.db.close()

    def add_item(self, item):
        dic = item.to_dict()
        self.db.insert(dic)

    def does_item_exist(self, item):
        item_id = item.item_id
        res = self.db.search(where('id')==item_id)
        if len(res) >= 1:
            return True

    def is_updated_or_new(self, item):
        item_id = item.item_id
        res = self.db.search(where('id')==item_id)
        if len(res) >= 1:
            res = res[0] # get the first and hopefully only member of the list
            if res['price'] == item.price:
                return False
        return True
