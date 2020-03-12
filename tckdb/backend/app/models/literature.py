"""
TCKDB backend app models literature module
"""

from sqlalchemy import Column, Integer, String

from tckdb.backend.app.db.base_class import Base


class Literature(Base):
    """
    A class for representing a TCKDB Literature item

    Attributes:
        id (int): The primary key.
        type (str): The Literature type. Allowed values are 'article', 'book', or 'thesis'.
        authors (str): The names of all authors (limited to 255 characters, use "et al." if needed).
        title (str): The article, thesis, or book title.
        year (int): The publication year.
        journal (str): The article journal.
        publisher (str): The book's publisher.
        volume (int): The journal volume.
        issue (int): The journal issue.
        page_start (int): The article starting page.
        page_end (int): The article ending page.
        editors (str): The book editors.
        edition (str): The book edition.
        chapter_title (str): The book's chapter title.
        publication_place (str): The book's publication place.
        advisor (str): The thesis advisor.
        doi (str): The article DOI.
        isbn (str): The book ISBN.
        url (str): The web address of the Literature source.
    """
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    type = Column(String(10), nullable=False)
    authors = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    year = Column(Integer, nullable=False)
    journal = Column(String(255))
    publisher = Column(String(255))
    volume = Column(Integer)
    issue = Column(Integer)
    page_start = Column(Integer)
    page_end = Column(Integer)
    editors = Column(String(255))
    edition = Column(String(50))
    chapter_title = Column(String(255))
    publication_place = Column(String(255))
    advisor = Column(String(255))
    doi = Column(String(255))
    isbn = Column(String(255))
    url = Column(String(500), nullable=False)

    def __repr__(self) -> str:
        repr_str = f"<{self.__class__.__name__}("
        repr_str += f"id={self.id}, "
        repr_str += f"type='{self.type}', "
        repr_str += f"authors='{self.authors}', "
        repr_str += f"title='{self.title}', "
        repr_str += f"year={self.year}, "
        if self.journal is not None:
            repr_str += f"journal='{self.journal}', "
        if self.publisher is not None:
            repr_str += f"publisher='{self.publisher}', "
        if self.volume is not None:
            repr_str += f"volume={self.volume}, "
        if self.issue is not None:
            repr_str += f"issue={self.issue}, "
        if self.page_start is not None:
            repr_str += f"page_start={self.page_start}, "
        if self.page_end is not None:
            repr_str += f"page_end={self.page_end}, "
        if self.editors is not None:
            repr_str += f"editors='{self.editors}', "
        if self.edition is not None:
            repr_str += f"edition='{self.edition}', "
        if self.chapter_title is not None:
            repr_str += f"chapter_title='{self.chapter_title}', "
        if self.publication_place is not None:
            repr_str += f"publication_place='{self.publication_place}', "
        if self.advisor is not None:
            repr_str += f"advisor='{self.advisor}', "
        if self.doi is not None:
            repr_str += f"doi='{self.doi}', "
        if self.isbn is not None:
            repr_str += f"isbn='{self.isbn}', "
        repr_str += f"url='{self.url}')>"
        return repr_str

    def __str__(self) -> str:
        if self.type == 'article':
            return f'{self.authors}, "{self.title}", {self.journal} {self.year}, {self.volume}({self.issue}), ' \
                   f'{self.page_start}-{self.page_end}. doi: {self.doi}'
        if self.type == 'book':
            return f'{self.authors}, "{self.chapter_title}", in: {self.editors} "{self.title}", {self.edition}, ' \
                   f'{self.publisher}, {self.publication_place} {self.year}. ISBN: {self.isbn}'
        if self.type == 'thesis':
            return f'{self.authors}, Dissertation title: "{self.title}", {self.year}, {self.publisher}, ' \
                   f'Advisor: {self.advisor}. URL: {self.url}'
