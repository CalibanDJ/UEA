# Exemple de lecteur de fichier Excel de voeux

import random
import array
import numpy as np
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
import sys

DEFAULTFILENAME = 'voeux-projets-semestriels-2021.xlsx'

PROJETSINDUSTRIELS = {'planif-contraintes', 'reporting-data'}

class ProblemHelper():
    ''' Handles the reading of the wishes and prepare most of the internal data structure for this problem '''

    def __init__(self, filename=DEFAULTFILENAME):
        self._buildMatrixFromExcel(filename)
        self.printProblem()

    def _buildMatrixFromExcel(self, filename):
        df = pd.read_excel(filename)

        studentsNumber = {}
        studentsGroup = {}
        studentsNumberToName = []
        voeux = {}
        voeuxOriginaux = {} # same matrix as Excel one
        projectsNumber = {}
        projectsNumberToName = []
        for col in df.columns[3:23]:
            projectsNumber[col] = len(projectsNumberToName)
            projectsNumberToName.append(col)
        for i in range(0,38):
            nom = df['Prénom'][i] + " " + df['Nom'][i]
            studentsNumber[nom] = len(studentsNumber)
            studentsGroup[i] = df['Ecole'][i]
            studentsNumberToName.append(nom)
            assert(studentsNumberToName[studentsNumber[nom]]==nom)
            voeux[nom] = [-1] * len(projectsNumberToName)
            voeuxOriginaux[nom] = []
            col = 0
            for j in df.columns[3:23]: # j is given by pandas: this is a column header (name of project)
                preference_project = df[j][i] # preference number for the student number i for the project name j
                if pd.isnull(preference_project): 
                    voeuxOriginaux[nom].append(3) # Hardcoded. Not scored = bad project
                    col += 1
                    continue # Pas de voeux exprimé
                preference_project = int(preference_project)
                voeuxOriginaux[nom].append(preference_project)
                voeux[nom][preference_project-1] = col # order starting at 0
                col += 1
        

        self._studentsNumber = studentsNumber
        self._studentsNumberToName = studentsNumberToName
        self._projectsNumber = projectsNumber
        self._projectsNumberToName = projectsNumberToName
        self._originalWishes = voeuxOriginaux
        self._studentsGroup = studentsGroup

    @staticmethod
    def printMatrix(m):
        paddingLeft = max([len(str(x)) for x in m]) + 2
        cellPadding = max([max([len(str(x)) for x in v]) for v in m.values()]) + 1
        print("\n".join([str(n).ljust(paddingLeft,'.') + " : " + " ".join([str(i).rjust(cellPadding) for i in m[n]]) for n in m]))
    
    def printProblem(self):
        print("Matrice originale des choix ordonnés par etudiant :")
        print("---------------------------------------------------")
        self.printMatrix(self._originalWishes)
        print()
        print("noms des projets")
        print("----------------")
        print(["{:02d}".format(i) + ": " + self._projectsNumberToName[i] for i in range(len(self._projectsNumberToName))])
        print()
        print("noms des étudiants")
        print("----------------")
        print([str(i)+": " + self._studentsNumberToName[i] for i in range(len(self._studentsNumberToName))])

    def getNbStudents(self):
        ''' Returns the total number of Students'''
        return len(self._studentsNumber)

    def getNbProjects(self):
        ''' Returns the total number of projects'''
        return len(self._projectsNumber)

    def matrixChoices(self):
        ''' Gets the matrix of choices M s.t. M[i] is the ordered list of project numbers for student i. M[i][j] is the jth prefered project for student i'''
        return self._matrixChoices

    def matrixStudentNameToNumber(self):
        ''' Return the matrix N of numbers of the students, N[X] is the internal number of student X (usually given "FirstName LastName"'''
        return self._studentsNumber

    def matrixStudentNumberToName(self):
        ''' Returns the matrix N of names of students, N[i] is the name of the student i'''
        return self._studentsNumberToName

    def matrixProjectsNameToNumber(self):
        return self._projectsNumber

    def matrixProjectsNumberToName(self):
        return self._projectsNumberToName
    
    def getPenaltiesNbStudentsPerProject(self, n):
        return self._penaltiesStudentsPerProject[n]

    def isEMMK(self, n):
        return (self._studentsGroup[n] == "EMMK")

    def getOriginalWish(self, n):
        name = self.studentsNumberToName[n]
        print('')
        return self._originalWishes[n]

