import typer
from app.database import create_db_and_tables, get_session, drop_all
from app.models import User
from fastapi import Depends
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_

cli = typer.Typer()

@cli.command()
def initialize():
    with get_session() as db: # Get a connection to the database
        drop_all() # delete all tables
        create_db_and_tables() #recreate all tables
        bob = User(username = 'bob', email = 'bob@mail.com', password = 'bobpass') # Create a new user (in memory)
        db.add(bob) # Tell the database about this new data
        db.commit() # Tell the database persist the data
        db.refresh(bob) # Update the user (we use this to get the ID from the db)
        print("Database Initialized")

@cli.command()
def get_user(username:str):
    with get_session() as db: # Get a connection to the database
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found!')
            return
        print(user)

@cli.command()
def get_all_users():
    with get_session() as db:
        all_users = db.exec(select(User)).all()
        if not all_users:
            print("No users found")
        else:
            for user in all_users:
                print(user)


@cli.command()
def change_email(username: str, new_email:str):
    with get_session() as db: # Get a connection to the database
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found! Unable to update email.')
            return
        user.email = new_email
        db.add(user)
        db.commit()
        print(f"Updated {user.username}'s email to {user.email}")

@cli.command()
def create_user(username: str, email:str, password: str):
    with get_session() as db: # Get a connection to the database
        newuser = User(username=username, email=email, password=password)
        try:
            db.add(newuser)
            db.commit()
        except IntegrityError as e:
            db.rollback() #let the database undo any previous steps of a transaction
            #print(e.orig) #optionally print the error raised by the database
            print("Username or email already taken!") #give the user a useful message
        else:
            print(newuser) # print the newly created user

@cli.command()
def delete_user(username: str):
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found! Unable to delete user.')
            return
        db.delete(user)
        db.commit()
        print(f'{username} deleted')
        
@cli.command()
def get_user_from_identifier(identifier: str = typer.Argument(..., help="Email or username to search for (partial match)")):
    """Search for a user by partial email or username match.""" # documentation for the command

    with get_session() as db:
        user = db.exec(select(User).where(or_(User.email.like(f'%{identifier}%'), User.username.like(f'%{identifier}%')))).first()
        if not user:
            print(f'{identifier} not found! Unable to find user.')
            return
        print(user)

@cli.command()
def list_users(limit: int = typer.Argument(10, help="Maximum number of users to display"),
    offset: int = typer.Argument(0, help="Number of users to skip from the start")
):
    """List the first N users of the database to be used by a paginated table.""" # documentation for the command

    with get_session() as db:
        users = db.exec(select(User).offset(offset).limit(limit)).all()
        if not users:
            print("No users found!")
            return
        for user in users:
            print(user)


if __name__ == "__main__":
    cli()
    
