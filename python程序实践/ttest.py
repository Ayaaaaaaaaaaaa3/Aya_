class Book:
    def __init__ (self,title:str,author:str,isbn:int,price:float):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.price = price
    def display_info(self):
        print(f"{self.title}  {self.author}  {self.isbn}  {self.price}")
class Library:
    def __init__(self):
        self.books = []
    def add_book(self, book:Book):
        self.books.append(book)
    def remove_book_by_isbn(self,isbn:int):
        self.books = [book for book in self.books if book.isbn != isbn]
    def find_book_by_title(self, title:str):
        for book in self.books:
            if book.title.lower() == title.lower():
                return book
        return None
    def find_book_by_author(self, author:str):
        for book in self.books:
            if book.author.lower() == author.lower():
                return book
        return None
    def sort_price(self):
        self.books.sort(key=lambda book: book.price)
    def display_all_books(self):
        for book in self.books:
            book.display_info()

# Example usage
if __name__ == "__main__":
    library = Library()
    book1 = Book("The Great Gatsby", "F. Scott Fitzgerald", 9780743273565, 10.99)
    book2 = Book("1984", "George Orwell", 9780451524935, 8.99)
    book3 = Book("To Kill a Mockingbird", "Harper Lee", 9780061120084, 7.99)
    book4 = Book("The Catcher in the Rye", "J.D. Salinger", 9780316769488, 9.99)
    book5 = Book("Pride and Prejudice", "Jane Austen", 9780141040349, 6.99)
    
    library.add_book(book1)
    library.add_book(book2)
    library.add_book(book3)
    library.add_book(book4)
    library.add_book(book5)
    
    print("All books in the library:")
    library.sort_price()
    library.display_all_books()
    
    library.remove_book_by_isbn(9780451524935)
    
    print("\nAfter removing a book:")
    library.display_all_books()