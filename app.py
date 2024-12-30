from Views.User_View import *
from tkinter import *
from database import Base, engine
from Controllers.Adruno_Controler import *

Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Lincense Plate")
    connect_arduino()
    first_screen(root, load_model, lambda: admin_view(root))
    root.mainloop()
    stopArduino()