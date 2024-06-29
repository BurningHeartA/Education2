import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror, showwarning, showinfo
import random
from tkinter import filedialog
import TestModule
import os
import time
import numpy as np
import matplotlib.pyplot as plt


FILENAME = ""
GEAR_SET = []

def ReadData(label=None, btn=None):
    global FILENAME, GEAR_SET
    filepath=filedialog.askopenfilename()
    if filepath!="":
        label.configure(text=os.path.basename(filepath))
        FILENAME = filepath
        f = open(FILENAME)
        GEAR_SET = [[int(i) for i in line.split()] for line in f]
        btn.configure(state=tk.NORMAL)

def set_all(SpinBoxes=None, num=None):
    for a in SpinBoxes:
        a.set(num)
def set_random(SpinBoxes=None):
    for a in SpinBoxes:
        a.set(random.randint(0, 4))
def set_random_singleset(SpinBoxes=None):
    set_all(SpinBoxes, 0)
    a = random.randint(20, 87)
    SpinBoxes[a - 20].set(int(SpinBoxes[a - 20].get()) + 1)
    b = random.randint(20, 100)
    SpinBoxes[b - 20].set(int(SpinBoxes[b - 20].get()) + 1)
    c = random.randint(20, 100)
    SpinBoxes[c - 20].set(int(SpinBoxes[c - 20].get()) + 1)
    d = random.randint(20, 100)
    SpinBoxes[d - 20].set(int(SpinBoxes[d - 20].get()) + 1)
def generate_file(SpinBoxes=None):
    i = 0
    name = ""
    num = SpinBoxes[i].get()
    if num > '0':
        name = name + num
    else:
        name = name + '_'
    count = 0
    while num == '0' and i < 80:
        i += 1
        num = SpinBoxes[i].get()
        if num > '0':
            name = name + num
        else:
            name = name + '_'
    if i > 67:
        showerror(title="Ошибка", message="Хотя бы одна шестерня должна быть меньше 88.")
    else:
        count += int(num)
        s = str(i + 20) + ' ' + num
        i += 1
        while i < len(SpinBoxes):
            num = SpinBoxes[i].get()
            if num > '0':
                count += int(num)
                s = s + '\n' + str(i + 20) + ' ' + num
                name = name + num
            else:
                name = name + '_'
            i += 1
        if count >= 4:
            f = open(name + '.txt', 'w')
            f.write(s)
            f.close()
        else:
            showerror(title="Ошибка", message="В наборе должны присутствовать минимум 4 шестерни")

def insertTableElement(res, method,Time, table):
    elem=[method]
    elem+=[str(Time)]
    #("Метод", "Время", "Сравнений", "Комбинаций", "Ответ", "Ошибка")
    elem+=[str(res.comparisons)]
    elem+=[str(res.combos)]
    if res.found:
        elem+=[str(res.Set)]
        elem+=[str(res.error)]
    else:
        elem += ["Не найдено"]
        elem += ["-"]
    table.insert("",tk.END,values=elem)

def Test(GearSet = None, RatioField=None, Table=None):
    ratioSTR = RatioField.get()
    ratio=0.0
    try:
        ratio = float(ratioSTR)
        if (ratio > 0.0 and ratio <= 25.0):
            for elem in Table.get_children():
                Table.delete(elem)
            #start_time=round(time.time()*1000000000)
            #Test_Brute = TestModule.BruteForce(GearSet, ratio)
            #end_time = round(time.time() * 1000000000)
            #test_time=float(end_time-start_time)/1000000
            #insertTableElement(Test_Brute,"Полный перебор", test_time, Table)

            start_time = round(time.time() * 1000000000)
            Test_Branch = TestModule.BranchAndBound(GearSet, ratio)
            end_time = round(time.time() * 1000000000)
            test_time = float(end_time - start_time) / 1000000
            insertTableElement(Test_Branch, "Ветвей и границ", test_time, Table)

            start_time = round(time.time() * 1000000000)
            Test_Greedy = TestModule.BruteForce(GearSet, ratio)
            end_time = round(time.time() * 1000000000)
            test_time = float(end_time - start_time) / 1000000
            insertTableElement(Test_Greedy, "Жадный алгоритм", test_time, Table)

        else:
            showerror(title="Ошибка", message="Передаточное число должно принадлежать промежутку (0;25]")
    except ValueError:
        showerror(title="Ошибка", message="Введенное значение не является числом.")

def main():
    root = tk.Tk()
    WinWidth = 1440
    WinHeight = 800
    root.title('CNC-GuitarCombinations')
    x = (root.winfo_screenwidth() - WinWidth) / 2
    y = (root.winfo_screenheight() - WinHeight) / 2
    root.wm_geometry("%dx%d+%d+%d" % (WinWidth, WinHeight, x, y))
    # root.geometry('1440x800')
    root.resizable(False, False)

    NB = ttk.Notebook(root)
    NB.pack(expand=True, fill='both')

    GeneratorFrame = ttk.Frame(NB, width=1000, height=400, padding=[5, -5])
    GeneratorFrame.pack(expand=True, fill='both')

    GearFrame = ttk.LabelFrame(GeneratorFrame, text="Шестерни")
    GearFrame.grid(row=0, column=0, rowspan=7, columnspan=1, sticky='news')

    GearValues = [0, 1, 2, 3, 4]
    SpinBoxes = []
    GearLabels = []
    for i in range(81):
        label = ttk.Label(GearFrame, text=str(20 + i))
        label.grid(row=(i % 9), column=(i // 9) * 2, sticky='e', padx=2, pady=2)
        spinbox = ttk.Spinbox(GearFrame, from_=0, to=4, width=3)
        spinbox.set(value=1)
        spinbox.grid(row=(i % 9), column=(i // 9) * 2 + 1, sticky='w', padx=(0, 5), pady=2)
        GearLabels.append(label)
        SpinBoxes.append(spinbox)
    GearFrame.columnconfigure(tuple(range(18)), weight=1)
    GearFrame.rowconfigure(tuple(range(9)), weight=1)
    ClearAllButton = ttk.Button(GeneratorFrame, text="Очистить", command=lambda: set_all(SpinBoxes, 0), width=30)
    ClearAllButton.grid(row=0, column=1, sticky='news')
    SetOneButton = ttk.Button(GeneratorFrame, text="Заполнить единицами", command=lambda: set_all(SpinBoxes, 1),
                              width=30)
    SetOneButton.grid(row=1, column=1, sticky='news')
    SetTwoButton = ttk.Button(GeneratorFrame, text="Заполнить двойками", command=lambda: set_all(SpinBoxes, 2),
                              width=30)
    SetTwoButton.grid(row=2, column=1, sticky='news')
    SetThreeButton = ttk.Button(GeneratorFrame, text="Заполнить тройками", command=lambda: set_all(SpinBoxes, 3),
                                width=30)
    SetThreeButton.grid(row=3, column=1, sticky='news')
    SetFourButton = ttk.Button(GeneratorFrame, text="Заполнить четверками", command=lambda: set_all(SpinBoxes, 4),
                               width=30)
    SetFourButton.grid(row=4, column=1, sticky='news')
    RandomSetButton = ttk.Button(GeneratorFrame, text="Рандомный набор", command=lambda: set_random(SpinBoxes),
                                 width=30)
    RandomSetButton.grid(row=5, column=1, sticky='news')
    RandomSingleSetButton = ttk.Button(GeneratorFrame, text="Единственный набор",
                                       command=lambda: set_random_singleset(SpinBoxes), width=30)
    RandomSingleSetButton.grid(row=6, column=1, sticky='news')
    GenerateButton = ttk.Button(GeneratorFrame, text="Сгенерировать тест", command=lambda: generate_file(SpinBoxes))
    GenerateButton.grid(row=7, column=0, columnspan=2, sticky='news')
    GeneratorFrame.columnconfigure(tuple(range(2)), weight=1)
    GeneratorFrame.rowconfigure(tuple(range(8)), weight=1)

    TestFrame = ttk.Frame(NB, width=1000, height=500, padding=[5, 5])
    TestFrame.pack(expand=True, fill='both')

    # Блок ввода передаточного числа и файла с набором шестерен
    RatioFrame = ttk.LabelFrame(TestFrame, text="Набор тестовых данных", padding=[5, 5])
    RatioFrame.grid(row=0, column=0, sticky='news', padx=5, pady=5, columnspan=1, rowspan=1)

    InputRatioLabel = ttk.Label(RatioFrame, text="Передаточное число:", width=20)
    InputRatioLabel.grid(row=0, column=0, sticky='w')

    RatioField = ttk.Entry(RatioFrame, width=15)
    RatioField.grid(row=0, column=1, sticky='we', columnspan=1)

    InputFileLabel = ttk.Label(RatioFrame, text="Набор шестерен:", width=20)
    InputFileLabel.grid(row=1, column=0, sticky='w', columnspan=1)

    FileNameLabel = ttk.Label(RatioFrame, text="Файл не выбран.", width=30, wraplength=0)
    FileNameLabel.grid(row=1, column=1, sticky='we')

    OpenFileButton = ttk.Button(RatioFrame, text="Выбрать файл с набором шестерен", command = lambda:ReadData(FileNameLabel, TestButton))
    OpenFileButton.grid(row=2, column=0, columnspan=2, sticky='news')

    TestButton = ttk.Button(RatioFrame, text="Провести тест", state=tk.DISABLED, command = lambda: Test(GEAR_SET,RatioField,Table))
    TestButton.grid(row=3, column=0, columnspan=2, sticky='news')

    RatioFrame.columnconfigure(0, weight=0)
    RatioFrame.columnconfigure(1, weight=1)
    RatioFrame.rowconfigure(tuple(range(4)), weight=1)

    TimeFrame = ttk.LabelFrame(TestFrame, text="Время выполнения", padding=[5, 5])
    TimeFrame.grid(row=1, column=0, sticky='news', padx=5, pady=5)

    CombosFrame = ttk.LabelFrame(TestFrame, text="Рассмотрено комбинаций", padding=[5, 5])
    CombosFrame.grid(row=1, column=1, sticky='news', padx=5, pady=5)

    ComparisonsFrame = ttk.LabelFrame(TestFrame, text="Количество сравнений", padding=[5, 5])
    ComparisonsFrame.grid(row=1, column=2, sticky='news', padx=5, pady=5)

    ResultFrame = ttk.LabelFrame(TestFrame, text="Результаты теста", padding=[5, 5])
    ResultFrame.grid(row=0, column=1, sticky='news', padx=5, pady=5, columnspan=2, rowspan=1)
    columns = ("Метод", "Время", "Сравнений", "Комбинаций", "Ответ", "Ошибка")
    Table = ttk.Treeview(ResultFrame, columns=columns, show="headings")
    Table.heading("Метод", text="Метод", anchor='w')
    Table.heading("Время", text="Время(мс)", anchor='w')
    Table.heading("Сравнений", text="Сравнений", anchor='w')
    Table.heading("Комбинаций", text="Комбинаций", anchor='w')
    Table.heading("Ответ", text="Ответ", anchor='w')
    Table.heading("Ошибка", text="Ошибка", anchor='w')
    Table.column("#1", stretch=tk.YES, width=200)
    Table.column("#2", stretch=tk.YES, width=100)
    Table.column("#3", stretch=tk.YES, width=100)
    Table.column("#4", stretch=tk.YES, width=100)
    Table.column("#5", stretch=tk.YES, width=100)
    Table.column("#6", stretch=tk.YES, width=100)
    TableDefaultValues = [("Полный перебор", "--.--", "-", "-", "-", "-"),
                          ("Ветвей и границ", "--.--", "-", "-", "-", "-"),
                          ("Жадный алгоритм", "--.--", "-", "-", "-", "-")]
    for method in TableDefaultValues:
        Table.insert("", tk.END, values=method)
    Table.pack(expand=True, fill='both')
    # TestFrame.columnconfigure(tuple(range(3)), weight=1)
    TestFrame.columnconfigure(0, weight=2)
    TestFrame.columnconfigure(1, weight=1)
    TestFrame.columnconfigure(2, weight=1)
    TestFrame.rowconfigure(0, weight=1)
    TestFrame.rowconfigure(1, weight=4)

    NB.add(GeneratorFrame, text='Генерация')
    NB.add(TestFrame, text='Тестирование')
    root.mainloop()


if __name__ == '__main__':
    main()
