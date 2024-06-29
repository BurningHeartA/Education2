import tkinter as tk
from tkinter import ttk


def ReadData():
    pass


def main():
    root = tk.Tk()
    root.title('CNC-GuitarCombinations')
    root.geometry('1000x700')

    NB = ttk.Notebook(root)
    NB.pack(expand=True, fill='both')

    GeneratorFrame = ttk.Frame(NB, width=1000, height=400, padding=[5, 5])
    GeneratorFrame.pack(expand=True, fill='both')

    GearValues = [0, 1, 2, 3, 4]
    SpinBoxes = []
    GearLabels = []
    for i in range(81):
        label = ttk.Label(GeneratorFrame, text=str(20 + i))
        label.grid(row=(i % 9), column=(i // 9)*2, sticky='e', ipadx =1)
        spinbox = ttk.Spinbox(GeneratorFrame, from_=0, to=4,width=3)
        spinbox.set(value=1)
        spinbox.grid(row=(i % 9), column=(i // 9)*2+1, sticky='w', ipadx =1)
        GearLabels.append(label)
        SpinBoxes.append(spinbox)
    GeneratorFrame.columnconfigure(tuple(range(18)),weight=1)
    GeneratorFrame.rowconfigure(tuple(range(9)),weight=1)
    TestFrame = ttk.Frame(NB, width=1000, height=500, padding=[5, 5])
    TestFrame.pack(expand=True, fill='both')
    NB.add(GeneratorFrame, text='Генерация')
    NB.add(TestFrame, text='Тестирование')
    root.mainloop()


if __name__ == '__main__':
    main()
