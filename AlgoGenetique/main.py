# This is a sample Python script.

# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from excelReader import ProblemHelper
import numpy as np
import random



def init_popu(problem):
    nb_student = problem.getNbStudents()
    popu = np.zeros(nb_student, dtype=np.int8)
    for i in range(problem.getNbStudents()) :
        popu[i] = random.randint(1, problem.getNbProjects())
    return popu

def fitness_score(problem, popu):
    rev_sol = np.zeros(problem.getNbProjects(), dtype=np.int8)
    mix = np.zeros(problem.getNbProjects(), dtype=np.int8)
    project_affection = np.zeros(problem.getNbProjects(), dtype=np.int8)

    for i in range(problem.getNbStudents()) :
        index_project = popu[i] - 1
        rev_sol[index_project] += 1

        if mix[index_project] != 3 :
            if problem.isEMMK(i) and mix[index_project] != 1 :
                mix[index_project] += 1
            elif not problem.isEMMK(i) and mix[index_project] != 2:
                mix[index_project] += 2

        project_affection[index_project] += problem.getOriginalWish(i)[index_project]
    return rev_sol, mix, project_affection


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    pb = ProblemHelper()
    popu = init_popu(pb)
    rev_sol, mix, project_affect = fitness_score(pb, popu)
    print(popu)
    print(rev_sol)
    print(mix)
    print(project_affect)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
