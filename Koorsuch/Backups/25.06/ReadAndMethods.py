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


# считывание набора шестерен
def ReadTest(filename):
    f = open(filename)
    GearSet = [[int(i) for i in line.split()] for line in f]
    return GearSet


# Сравнивать результаты работы методов будем по
class MethodResult:
    def __init__(self, comparisons, combos, Set, ratio, error, found):
        self.checks = comparisons
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
    angle_min = max(ANGLE_MIN, math.acos((WALL - b) / AB))
    C_MinMax = [max(CD_distance(AB, ANGLE_MAX) - GEAR_MAX, GEAR_MIN),
                min(CD_distance(AB, angle_min) - GEAR_MIN, WALL - AB * math.cos(ANGLE_MAX))]
    return C_MinMax


def Branch_D(AB, b, c):
    angle_min = max(ANGLE_MIN, math.acos((WALL - max(b, c)) / AB))
    D_MinMax = [max(CD_distance(AB, ANGLE_MAX) - c, GEAR_MIN),
                min(CD_distance(AB, angle_min) - c, GEAR_MAX)]
    return D_MinMax


# Метод полного перебора - берем возможный набор из 4 шестерен, проверяем на совместимость, выбираем набор с минимальной ошибкой
def BruteForce(Gears, ratio):
    le = len(Gears)
    Combos = 0
    Comparisons = 0
    Error = 100.0
    CurrentCombo = [1, 1, 1, 1]
    CorrectCombo = [1, 1, 1, 1]
    FoundCorrectCombo = False
    CurrentRatio = 100.0
    CorrectRatio = 100.0
    CurrentError = 1.0
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
                                Comparisons += 1
                                CurrentError = abs(CurrentRatio - ratio) / ratio
                                if CurrentError < Error:
                                    Comparisons += 1
                                    if Condition_A(Gears[i][0]):
                                        CurrentCombo = [Gears[i][0], Gears[j][0], Gears[k][0], Gears[l][0]]
                                        Check = CheckSet(CurrentCombo)
                                        Comparisons += Check[1]
                                        Comparisons += 1
                                        if Check[0]:
                                            FoundCorrectCombo=True
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
    Error = 100.0
    CurrentCombo = [1, 1, 1, 1]
    CorrectCombo = [1, 1, 1, 1]
    FoundCorrectCombo = False
    CurrentRatio = 100.0
    CorrectRatio = 100.0
    CurrentError = 1.0

    i=0
    Comparisons+=1
    while (Condition_A(Gears[i][0]) and i<le):
        Gears[i][1] -= 1
        j=0
        B_MinMax=Branch_B(Gears[i][0])
        Comparisons+=1
        if B_MinMax[0]<=B_MinMax[1]:
            Comparisons+=1
            while (Gears[j][0]<B_MinMax[0] and j<le):
                j+=1
                Comparisons+=1
            Comparisons+=1
            while (Gears[j][0]<=B_MinMax[1] and j<le):
                Comparisons+=1
                if Gears[j][1]>0:
                    Gears[j][1] -= 1
                    
        Gears[i][1] += 1
        i+=1
        Comparisons+=1

    Res = MethodResult(Comparisons, Combos, CorrectCombo, CorrectRatio, Error, FoundCorrectCombo)
    return Res


# Жадный алгоритм
def GreedyAlgorithm(Gears, ratio):
    return
