
def CreateTable(QueryCurs):
    QueryCurs.execute('''CREATE TABLE IF NOT EXISTS Image
    (id INTEGER PRIMARY KEY,Path TEXT, Tag1 TEXT, Tag2 TEXT, Tag3 TEXT, Tag4 TEXT, Tag5 TEXT)''')

def AddEntry(QueryCurs,Path,Tag1,Tag2,Tag3,Tag4,Tag5):
    QueryCurs.execute('''INSERT INTO Image (Path,Tag1,Tag2,Tag3,Tag4,Tag5)
    VALUES (?,?,?,?,?,?)''',(Path,Tag1,Tag2,Tag3,Tag4,Tag5))

def GetImageWithFilter(QueryCurs, Tag):
    QueryCurs.execute("SELECT Path FROM Image WHERE Tag1 = ? OR Tag2 = ?  OR Tag3 = ?  OR Tag4 = ?  OR Tag5 = ?", (Tag,Tag,Tag,Tag,Tag,))
    imagesList = []    
    for data in QueryCurs:
        imagesList.append(data[0])
    return imagesList

def ImageExist(QueryCurs,Path):
    QueryCurs.execute("SELECT 1 FROM Image WHERE Path=?", (Path,))
    for i in QueryCurs:
        if i[0] == 1 :
            return True
        else:
            return False
