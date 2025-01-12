from sqliteorm_py.basemodel import BaseModel
from sqliteorm_py.fields import CharField, IntegerField, TextField


class User(BaseModel):
    table_name = "users"  
    id = IntegerField(primary_key=True, autoincrement=True) 
    user_id = IntegerField()
    first_name = CharField(max_length=100)
    username = CharField(max_length=100, null=True, blank=True)



class Note(BaseModel):
    table_name = "notes"  
    id = IntegerField(primary_key=True, autoincrement=True) 
    user_id = IntegerField()
    title = CharField(max_length=50) 
    description = TextField()
    
