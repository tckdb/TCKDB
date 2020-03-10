"""
TCKDB backend app models author module
"""

from sqlalchemy import Column, Integer, String

from tckdb.backend.app.db.base_class import Base


class Author(Base):
    """
    A class for representing a TCKDB Author
    """
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    affiliation = Column(String(255), nullable=False)

    def __repr__(self):
        return f'<{self.__name__}(name={self.name}, email={self.email}, affiliation={self.affiliation})>'
