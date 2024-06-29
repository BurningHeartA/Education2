import math

ANGLE_MIN = 14.5 * math.pi / 180
ANGLE_MAX = 47.0 * math.pi / 180
AD = 158.0
AB_MIN = 86
AB_MAX = 146
A_MAX = 88
WALL = 203.0
GEAR_MIN = 20
GEAR_MAX = 100
ERROR_MAX = 0.1


# считывание набора шестерен
def ReadTest(filename):
    f = open(filename)
    GearSet = [[int(i) for i in line.split()] for line in f]
    return GearSet


# Сравнивать результаты работы методов будем по
class MethodResult:
    def __init__(self, comparisons, combos, Set, ratio, error, found):
        self.comparisons = comparisons
        self.combos = combos
        self.Set = Set.copy()
        self.ratio = ratio
        self.error = error
        self.found = found


# Условия на набор шестерен для жадного алгоритма и метода полного перебора

# Условие на первую шестерню, чтобы она не касалась нижней стенки
def Condition_A(a):
    return a <= A_MAX


# Условие на сцепляемость шестерен A и B, ограничение по устройству гитары
def Condition_AB(ab):
    return (ab >= AB_MIN and ab <= AB_MAX)


# Расстояние между шестернями С и D при заданном угле поворота гитары
def CD_distance(AB, angle):
    x_coord_squared = (math.cos(angle) * AB) ** 2
    y_coord_squared = (math.sin(angle) * math.sin(angle) * AB - AD) ** 2
    return math.sqrt(x_coord_squared + y_coord_squared)


# Условие на сцепляемость 3 и 4 шестерен
def Condition_CD(AB, CD):
    CD_MAX = CD_distance(AB, ANGLE_MIN)
    CD_MIN = CD_distance(AB, ANGLE_MAX)
    return (CD > CD_MIN and CD < CD_MAX)


def Condition_Wall(AB, CD, b, c):
    angle = math.pi / 2 - math.acos((AB * AB + AD * AD - CD * CD) / (2 * AB * AD))
    BC = max(b, c)
    return (BC + AB * math.cos(angle)) <= WALL


# Проверка на совместимость (полная), возращающая [истина=1/ложь=0, количество сравнений]
def CheckSet(Set):
    if not Condition_A(Set[0]):
        return [0, 1]
    AB = Set[0] + Set[1]
    if not Condition_AB(AB):
        return [0, 2]
    CD = Set[2] + Set[3]
    if not Condition_CD(AB, CD):
        return [0, 3]
    if not Condition_Wall(AB, CD, Set[1], Set[2]):
        return [0, 4]
    return [1, 4]


#########################################################################################################

# Условия на отдельные шестерни для метода ветвей и границ
def Branch_A(a):
    return a < A_MAX


def Branch_B(a):
    B_MinMax = [max(AB_MIN - a, GEAR_MIN), min(AB_MAX - a, GEAR_MAX)]
    return B_MinMax


def Branch_C(AB, b):
    angle_min = max(ANGLE_MIN, math.acos(min((WALL - b) / AB, 1)))
    C_MinMax = [math.ceil(max(CD_distance(AB, ANGLE_MAX) - GEAR_MAX, GEAR_MIN)),
                math.floor(min(CD_distance(AB, angle_min) - GEAR_MIN, WALL - AB * math.cos(ANGLE_MAX), GEAR_MAX))]
    return C_MinMax


def Branch_D(AB, b, c):
    angle_min = max(ANGLE_MIN, math.acos(min((WALL - max(b, c)) / AB, 1)))
    D_MinMax = [math.ceil(max(CD_distance(AB, ANGLE_MAX) - c, GEAR_MIN)),
                math.floor(min(CD_distance(AB, angle_min) - c, GEAR_MAX))]
    return D_MinMax


# Метод полного перебора - берем возможный набор из 4 шестерен, проверяем на совместимость, выбираем набор с минимальной ошибкой
def BruteForce(Gears, ratio):
    le = len(Gears)
    Combos = 0
    Comparisons = 0
    Error = ERROR_MAX
    CurrentCombo = [1, 1, 1, 1]
    CorrectCombo = [1, 1, 1, 1]
    FoundCorrectCombo = False
    CurrentRatio = 100.0
    CorrectRatio = 100.0
    CurrentError = ERROR_MAX
    for i in range(le):
        Gears[i][1] -= 1
        for j in range(le):
            Comparisons += 1
            if Gears[j][1] > 0:
                Gears[j][1] -= 1
                for k in range(le):
                    Comparisons += 1
                    if Gears[k][1] > 0:
                        Gears[k][1] -= 1
                        for l in range(le):
                            Comparisons += 1
                            if Gears[l][1] > 0:
                                CurrentRatio = Gears[i][0] * Gears[k][0] / (Gears[j][0] * Gears[l][0])
                                Combos += 1
                                CurrentError = abs(CurrentRatio - ratio) / ratio
                                Comparisons += 1
                                if CurrentError < Error:
                                    CurrentCombo = [Gears[i][0], Gears[j][0], Gears[k][0], Gears[l][0]]
                                    Check = CheckSet(CurrentCombo)
                                    Comparisons += Check[1] + 1
                                    if Check[0]:
                                        FoundCorrectCombo = True
                                        CorrectCombo = CurrentCombo.copy()
                                        CorrectRatio = CurrentRatio
                                        Error = CurrentError
                        Gears[k][1] += 1
                Gears[j][1] += 1
        Gears[i][1] += 1
    Res = MethodResult(Comparisons, Combos, CorrectCombo, CorrectRatio, Error, FoundCorrectCombo)
    return Res


# Метод ветвей и границ - набираем по одной только те шестерни, которые в теории могут дать совместимый набор
def BranchAndBound(Gears, ratio):
    le = len(Gears)
    Combos = 0
    Comparisons = 0
    Error = ERROR_MAX
    CurrentCombo = [1, 1, 1, 1]
    CorrectCombo = [1, 1, 1, 1]
    FoundCorrectCombo = False
    CurrentRatio = 100.0
    CorrectRatio = 100.0
    CurrentError = ERROR_MAX
    i = 0
    NextA = True
    while (i < le and NextA):
        Comparisons += 1
        if (Condition_A(Gears[i][0])):
            Gears[i][1] -= 1
            B_MinMax = Branch_B(Gears[i][0])
            Comparisons += 1
            if B_MinMax[0] <= B_MinMax[1] and B_MinMax[0] <= Gears[le - 1][0] and B_MinMax[1] >= Gears[0][0]:
                j = 0
                NextB = True
                while (j < le and NextB):
                    Comparisons += 1
                    if Gears[j][0] >= B_MinMax[0] and Gears[j][1] > 0:
                        Comparisons += 1
                        if Gears[j][0] <= B_MinMax[1]:
                            Gears[j][1] -= 1
                            AB = Gears[i][0] + Gears[j][0]
                            C_MinMax = Branch_C(AB, Gears[j][0])
                            Comparisons += 1
                            if C_MinMax[0] <= C_MinMax[1] and C_MinMax[0] <= Gears[le - 1][0] and C_MinMax[1] >= \
                                    Gears[0][0]:
                                k = 0
                                NextC = True
                                while (k < le and NextC):
                                    Comparisons += 1
                                    if Gears[k][0] >= C_MinMax[0] and Gears[k][1] > 0:
                                        Comparisons += 1
                                        if Gears[k][0] <= C_MinMax[1]:
                                            Gears[k][1] -= 1
                                            D_MinMax = Branch_D(AB, Gears[j][0], Gears[k][0])
                                            Comparisons += 1
                                            if D_MinMax[0] <= D_MinMax[1] and D_MinMax[0] <= Gears[le - 1][0] and \
                                                    D_MinMax[1] >= Gears[0][0]:
                                                l = 0
                                                NextD = True
                                                while (l < le and NextD):
                                                    Comparisons += 1
                                                    if Gears[l][0] >= D_MinMax[0] and Gears[l][1] > 0:
                                                        Comparisons += 1
                                                        if Gears[l][0] <= D_MinMax[1]:
                                                            CurrentRatio = (Gears[i][0] * Gears[k][0]) / (
                                                                    Gears[j][0] * Gears[l][0])
                                                            CurrentError = abs(CurrentRatio - ratio) / ratio
                                                            Combos += 1
                                                            Comparisons += 1
                                                            if CurrentError < Error:
                                                                FoundCorrectCombo = True
                                                                Error = CurrentError
                                                                CorrectCombo = [Gears[i][0], Gears[j][0], Gears[k][0],
                                                                                Gears[l][0]]
                                                                CorrectRatio = CurrentRatio
                                                        else:
                                                            NextD = False
                                                    l += 1
                                            Gears[k][1] += 1
                                        else:
                                            NextC = False
                                    k += 1
                            Gears[j][1] += 1
                        else:
                            NextB = False
                    j += 1
            Gears[i][1] += 1
        else:
            NextA = False
        i += 1
    Res = MethodResult(Comparisons, Combos, CorrectCombo, CorrectRatio, Error, FoundCorrectCombo)
    return Res


############################################################################################################
# Генерация возможных попарных передаточных чисел
def GenerateRatios(Gears):
    le = len(Gears)
    Ratios = []
    for i in range(le):
        for j in range(le):
            if ((not (i == j)) or Gears[i][1] > 1):
                Ratios += [[Gears[i][0] / Gears[j][0], Gears[i][0], Gears[j][0]]]
    Ratios = sorted(Ratios, key=lambda x: x[0])
    Ratios_compact = []
    k = 0
    Ratios_compact += [[Ratios[0][0], 1]]
    Ratios_compact[0] += [[Ratios[0][1], Ratios[0][2]]]
    i = 1
    while i < len(Ratios):
        if Ratios_compact[k][0] == Ratios[i][0]:
            Ratios_compact[k][1] += 1
            Ratios_compact[k] += [[Ratios[i][1], Ratios[i][2]]]
        else:
            Ratios_compact += [[Ratios[i][0], 1]]
            k += 1
            Ratios_compact[k] += [[Ratios[i][1], Ratios[i][2]]]
        i += 1
    return Ratios_compact  # Ratios


# Бинарный поиск по массиву передаточных чисел
def BinSearch(Ratios, ratio, left, right):
    l = left
    r = right  # len(Ratios) - 1
    if ratio <= Ratios[l][0]:
        return l
    if ratio >= Ratios[r][0]:
        return r
    while r - l > 1:
        mid = (l + r) // 2
        if ratio <= Ratios[mid][0]:
            r = mid
        else:
            l = mid
    if abs(ratio - Ratios[l][0]) < abs(ratio - Ratios[r][0]):
        return l
    return r


# Проверка существования комбинации в текущем наборе шестерен
def Exists(Combo, Dict):
    if Combo.count(Combo[0]) < Dict[Combo[0]]:
        return [0, 1]
    if Combo.count(Combo[1]) < Dict[Combo[1]]:
        return [0, 2]
    if Combo.count(Combo[2]) < Dict[Combo[2]]:
        return [0, 3]
    if Combo.count(Combo[3]) < Dict[Combo[3]]:
        return [0, 4]
    return [1, 4]


# Проверка совместимости пар шестеренок с одинаковым передаточным числом (между соответствующими парами)
def CheckSingleRatio(Ratios, l, r, GearDict):
    Combos = 0
    Comparisons = 0
    CurrentCombo = [1, 1, 1, 1]
    CorrectCombo = [1, 1, 1, 1]
    Found = False
    m = 0
    left_len = Ratios[l][1]
    right_len = Ratios[r][1]
    while (m < left_len and not Found):
        n = 0
        while (n < right_len and not Found):
            # abcd
            CurrentCombo = [Ratios[l][2 + m][0], Ratios[l][2 + m][1], Ratios[r][2 + n][0], Ratios[r][2 + n][1]]
            Exist = Exists(CurrentCombo, GearDict)
            Comparisons += Exist[1] + 1
            if Exist[0]:
                Check = CheckSet(CurrentCombo)
                Combos += 1
                Comparisons += Check[1] + 1
                if Check[0]:
                    Found = True
                    CorrectCombo = CurrentCombo.copy()
                else:
                    # cbad
                    CurrentCombo = [Ratios[r][2 + n][0], Ratios[l][2 + m][1], Ratios[l][2 + m][0], Ratios[r][2 + n][1]]
                    Check = CheckSet(CurrentCombo)
                    Combos += 1
                    Comparisons += Check[1] + 1
                    if Check[0]:
                        Found = True
                        CorrectCombo = CurrentCombo.copy()
                    else:
                        # cdab
                        CurrentCombo = [Ratios[r][2 + n][0], Ratios[r][2 + n][1], Ratios[l][2 + m][0],
                                        Ratios[l][2 + m][1]]
                        Check = CheckSet(CurrentCombo)
                        Combos += 1
                        Comparisons += Check[1] + 1
                        if Check[0]:
                            Found = True
                            CorrectCombo = CurrentCombo.copy()
                        else:
                            # adcb
                            CurrentCombo = [Ratios[l][2 + m][0], Ratios[r][2 + n][1], Ratios[r][2 + n][0],
                                            Ratios[l][2 + m][1]]
                            Check = CheckSet(CurrentCombo)
                            Combos += 1
                            Comparisons += Check[1] + 1
                            if Check[0]:
                                Found = True
                                CorrectCombo = CurrentCombo.copy()
            n += 1
        m += 1
    return [Combos, Comparisons, Found, CorrectCombo]


# Жадный алгоритм - берем сразу пару шестерен AB с передаточным числом (близким к искомому),
# а потом корректируем, пока не найдем совместимый набор с требуемой ошибкой.
def GreedyAlgorithm(Gears, ratio):
    GearDict = {a[0]: a[1] for a in Gears}
    Combos = 0
    Comparisons = 0
    Error = ERROR_MAX
    CurrentCombo = [1, 1, 1, 1]
    CorrectCombo = [1, 1, 1, 1]
    SingleRes = []
    Found = False
    CurrentRatio = 1.0
    CorrectRatio = 1.0
    CurrentError = ERROR_MAX
    # Предварительно составим вспомогательный массив передаточных чисел пар [ratio, count, [a1, b1], ..., [a_count,b_count]]
    Ratios = GenerateRatios(Gears)
    le = len(Ratios)
    i = BinSearch(Ratios, ratio, 0, le - 1)
    InvertedRatio = ratio / Ratios[i][0]
    j = BinSearch(Ratios, InvertedRatio, 0, le - 1)
    CurrentRatio = Ratios[i][0] * Ratios[j][0]
    CurrentError = abs(CurrentRatio - ratio) / ratio
    l = i
    r = j
    Comparisons += 1
    if CurrentError < Error:
        Check = CheckSingleRatio(Ratios, l, r, GearDict)
        Combos += Check[0]
        Comparisons += Check[1] + 1
        if Check[2]:
            Found = True
            CorrectCombo = Check[3]
            CorrectRatio = CurrentRatio
            Error = CurrentError
    while (l > 0):
        l -= 1
        InvertedRatio = ratio / Ratios[l][0]
        r = BinSearch(Ratios, InvertedRatio, 0, le - 1)
        CurrentRatio = Ratios[l][0] * Ratios[r][0]
        CurrentError = abs(CurrentRatio - ratio) / ratio
        Comparisons += 1
        if CurrentError < Error:
            Check = CheckSingleRatio(Ratios, l, r, GearDict)
            Combos += Check[0]
            Comparisons += Check[1] + 1
            if Check[2]:
                Found = True
                CorrectCombo = Check[3]
                CorrectRatio = CurrentRatio
                Error = CurrentError
    l = i
    while (l < le - 1):
        l += 1
        InvertedRatio = ratio / Ratios[l][0]
        r = BinSearch(Ratios, InvertedRatio, 0, le - 1)
        CurrentRatio = Ratios[l][0] * Ratios[r][0]
        CurrentError = abs(CurrentRatio - ratio) / ratio
        Comparisons += 1
        if CurrentError < Error:
            Check = CheckSingleRatio(Ratios, l, r, GearDict)
            Combos += Check[0]
            Comparisons += Check[1] + 1
            if Check[2]:
                Found = True
                CorrectCombo = Check[3]
                CorrectRatio = CurrentRatio
                Error = CurrentError
    Res = MethodResult(Comparisons, Combos, CorrectCombo, CorrectRatio, Error, Found)
    return Res