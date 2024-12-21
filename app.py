from Views.User_View import *
from tkinter import *
from database import Base, engine

Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Lincense Plate")
    first_screen(root, load_model, lambda: login_form(root))
    root.mainloop()