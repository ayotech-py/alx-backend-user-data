#!/usr/bin/env python3

"""DB module
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from user import User
from user import Base
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import InvalidRequestError

class DB:
    """
    DB class
    """

    def __init__(self) -> None:
        """Initialize a new DB instance
        """
        self._engine = create_engine("sqlite:///a.db", echo=True)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """Memoized session object
        """
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """Add a new user to the database

        Args:
            email (str): The user's email address
            hashed_password (str): The user's hashed password

        Returns:
            User: The newly created User object
        """
        user = User(email=email, hashed_password=hashed_password)
        self._session.add(user)
        self._session.commit()
        return user

    def find_user_by(self, **kwargs) -> User:
        """Find the first user that matches the provided filter criteria

        Args:
            **kwargs: Arbitrary keyword arguments that are used as filters for the query

        Returns:
            User: The first User object that matches the filter criteria

        Raises:
            NoResultFound: If no results are found that match the provided filter criteria
            InvalidRequestError: If the provided filter criteria are invalid
        """
        try:
            user = self._session.query(User).filter_by(**kwargs).first()
            if user is None:
                raise NoResultFound()
            return user
        except InvalidRequestError as e:
            self._session.rollback()
            raise e
        except NoResultFound as e:
            self._session.rollback()
            raise e

    def update_user(self, user_id: int, **kwargs) -> None:
        """Update a user in the database with the provided keyword arguments

        Args:
            user_id (int): The ID of the user to update
            **kwargs: Arbitrary keyword arguments that are used to update the user's attributes

        Raises:
            ValueError: If an argument that does not correspond to a user attribute is passed
        """
        try:
            user = self.find_user_by(id=user_id)
            for attr, value in kwargs.items():
                if hasattr(user, attr):
                    setattr(user, attr, value)
                else:
                    raise ValueError(f"Invalid user attribute: {attr}")
            self._session.commit()
        except (NoResultFound, InvalidRequestError) as e:
            self._session.rollback()
            raise e
