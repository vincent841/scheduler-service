import pickledb

db = pickledb.load("test.db", True)
db.set("name", "jinwon")
print(db.get("name"))
