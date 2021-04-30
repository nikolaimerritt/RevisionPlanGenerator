from math import sqrt
import scipy.optimize 
import datetime
import math

def printRevisionTimetable(rev, timeNames, examNames):
    prevTime = -1
    for i in range(len(rev)):
        time, exam = idxToTimeAndExam(numExams(rev), i)
        if time > prevTime:
            print("\n\nUntil", timeNames[time])
            prevTime = time
        print(examNames[exam] + ":", int(rev[i]), end="\t\t")
    print()


def idxToTimeAndExam(numExams, idx):
    # matrix cols are like
    # [r_0 0  r_0 1 ..  r_0 n-1]   [r_1 1   r_1 2 .. r_1 n-1]   [r_2 2 .. ]
    # different `segments` are in brackets

    # how long is our segment?
    displacement = idx
    lengthOfSegment = numExams
    while displacement >= lengthOfSegment and lengthOfSegment > 0:
        displacement -= lengthOfSegment
        lengthOfSegment -= 1
    
    time = numExams - lengthOfSegment
    exam = time + displacement
    return (time, exam)


def timeOfIdx(numExams, idx):
    return idxToTimeAndExam(numExams, idx)[0]


def examOfIdx(numExams, idx):
    return idxToTimeAndExam(numExams, idx)[1]


def numExams(rev):
    # L = length(rev) = n (n + 1) / 2 where n is number of exams
    # <==> n^2 + n - 2L = 0
    return int( (-1 + sqrt(1 + 8 * len(rev) )) / 2 )


def timeSpentEachDayInPeriodT(t, rev):
    return sum(rev[i] for i in range(len(rev)) if timeOfIdx(numExams(rev), i) == t)


def timeSpentRevisingForExam(times, exam, rev):
    n = numExams(rev)
    return sum(
        times[timeOfIdx(n, i)] * rev[i]
            for i in range(len(rev)) 
            if examOfIdx(n, i) == exam
    )


def constraintForPeriodT(times, minsPerDay, t):
    return {
        "type": "eq", # equal to 0
        "fun": lambda rev: timeSpentEachDayInPeriodT(t, rev) - minsPerDay
    }

def constraints(times, minsPerDay):
    return [constraintForPeriodT(times, minsPerDay, t) for t in range(len(times))]


def toMinimise(times, rev):
    # aiming to have total revision the same for all exams, so
    # minimising squared difference between total revision for exam i and for exam i+1
    return sum(
        (timeSpentRevisingForExam(times, i, rev) - 
            timeSpentRevisingForExam(times, i+1, rev)) ** 2
        for i in range(numExams(rev)-1)
    )


def revToStartSearchingAt(times, minsPerDay):
    n = len(times)
    return [0 for i in range(int(n * (n + 1) / 2))]


def findRevByMinimisation(times, minsPerDay):
    n = len(times)
    return scipy.optimize.basinhopping(
        func = lambda rev: toMinimise(times, rev), 
        x0 = revToStartSearchingAt(times, minsPerDay),
        minimizer_kwargs = {
            "bounds": [(0, minsPerDay) for i in range(int(n * (n+1) / 2))], 
            "method": "SLSQP", 
            "constraints": constraints(times, minsPerDay) 
        }
    ).x  



def times_TimeNames_ExamNames():
    times = []
    timeNames = []
    examNames = []
    
    dateBit = input("When do you plan to start revising?\nInput this like `day`/`month`, e.g. 24/5\nor simply \"today\"\n>\t")
    prevDate = datetime.datetime.today().date() \
        if dateBit == "today" else \
        datetime.date(2021, int(dateBit.split("/")[1]), int(dateBit.split("/")[0]))

    print("\nList your exams in order of how soon they are, like `exam-name`, `day`/`month` e.g.")
    print("Coding Theory, 24/5")
    print("When you want to see your timetable, enter \"timetable please\" instead")
    
    userInput = ""
    while True:
        userInput = input(">\t")
        if userInput != "timetable please":
            examNames.append(userInput.split(",")[0])
        
            dateBit = userInput.split(", ")[1]
            timeNames.append(dateBit)
            date = datetime.date(2021, int(dateBit.split("/")[1]), int(dateBit.split("/")[0]))
            times.append((date - prevDate).days)

            prevDate = date
        else:
            break

    return times, timeNames, examNames


def main():
    #times, timeNames, examNames = times_TimeNames_ExamNames()
    times = [x for x in [5, 2, 8, 5, 1]]
    timeNames = ['24/5', '26/5', '3/6', '8/6', '9/6']
    examNames = ['Finance', 'Bio', 'Coding', 'Symmetry', 'Quantum']

    minsPerDay = 240 # int(input("\nHow many minutes will you study per day?\n>\t"))
    reviseOnExamDay = True # "y" in input("\nAnd will you be revising on exam days?\n>\t").lower()
    
    print("Your study plan is...")
    rev = findRevByMinimisation(times, minsPerDay)
    print("minimised to", toMinimise(times, rev))
    printRevisionTimetable(rev, timeNames, examNames)

main()