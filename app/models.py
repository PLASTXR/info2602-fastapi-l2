from sqlmodel import Field, SQLModel
from typing import Optional
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

class User(SQLModel, table=True):
    id: Optional[int] =  Field(default=None, primary_key=True)
    username:str = Field(index=True, unique=True)
    email:str = Field(index=True, unique=True)
    password:str
    
    def __int__(self, username: str, email: str, passwod: str):
        self.username = username
        self.email = email
        self.set_password(passwod) # hash the password before storing it
    
    def set_password(self, password: str): # hash the password before storing it
        self.password = password_hash.hash(password)
        
    def __str__(self):
        return f"User(id={self.id}, username={self.username}, email={self.email})"