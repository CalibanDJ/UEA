import random
import sys, math

import numpy as np
import pygame
import pygame.draw

__circuit__ = ((35,30),(35,70),(200, 140),(340,220),(340,260),
               (200,300), (100,440), (120, 540), (180,580), (340,620), (480,570),
               (600, 440),
               (600, 70), (540, 30))


__car_size__ = [4, 6, 8, 10]
__car_color__ = ((0, 0, 255), (0, 255, 0), (255, 0, 0), (255, 255, 255))

__screenSize__ = (720,720)
__reaching__ = 20


# Utility functions for handling points
# I should probably build a class of vectors
def vecDiff(v1,v2):
    return (v1[0]-v2[0],v1[1]-v2[1])
def vecAdd(v1,v2):
    return (v2[0]+v1[0],v2[1]+v1[1])
def vecScalarMult(v, s):
    return (v[0]*s, v[1]*s)
def vecDot(v1, v2):
    return v1[0]*v2[0]+v1[1]*v2[1];
def vecInter(scalar, v1, v2):
    return (v1[0]+scalar*(v2[0]-v1[0]), v1[1]+scalar*(v2[1]-v2[0]))
def approximateLength(v1):
    '''This should be rewritten with an approximate length function (approximating it with no sqrt calls)'''
    return math.sqrt(v1[0]**2+v1[1]**2)
def approximateDistance(v1,v2):
    return approximateLength(vecDiff(v1,v2))


# Handles Vehicules
class Vehicule:
    _leader = 0
    _car_type = 0
    _coords = (0,0)   # vector
    _speed = (2,4)    # vector
    _maxspeed = 20 
    _force = (0,0)  # accelerating force
    _maxforce = 10
    _color = (200,100,100)
    _colorfg = tuple([int(c/2) for c in _color])
    _radius = 6
    _seeInFuture = 3


    def __init__(self, coords=(0,0), speed=(1,1), force =(1,1)):
        self._car_type = random.randint(0, 3)
        self._radius = __car_size__[self._car_type]
        self._color = __car_color__[self._car_type]
        self._coords = coords
        self._speed = speed
        self._force = force
        self._maxspeed = - self._radius + 20  # scale speed on size

    # reset speed on size
    def setDefaultMaxSpeed(self):
        self._maxspeed = - 2 * self._radius + 30

    def position(self): return self._pos

    def steerUpdate(self, track, vehicules):
        self._force = (0,0)
        self._force = vecAdd(self._force, self.steerPathFollow(track))

    def steerPathFollow(self, track):
        (s,p,l) = track._closestSegmentPointToPoint(self._coords)
        # TODO: We should first add a force if l is too large (too far from the middle of the track) 
        # This is the future position
        (sf, futurePosition) = track._segmentPointAddLength(s, p, max(10,approximateLength(self._speed)) * self._seeInFuture)
        # We just have to register a force to get to futurePosition !
        force = vecDiff(futurePosition, self._coords)
        force = vecScalarMult(force, self._maxforce/approximateLength(force))
        return force

    def drawMe(self, screen):
        pygame.draw.circle(screen,self._color,   self._coords, self._radius,0)
        pygame.draw.circle(screen,self._colorfg, self._coords, self._radius,1)


class SetOfVehicules:
    _vehicules = []

    def handleCollisions(self):
        " Simple collision checking. Not a very good one, but may do the job for simple simulations"
        for i,v1 in enumerate(self._vehicules):
            for v2 in self._vehicules[i+1:]:
                offset = vecDiff(v2._coords, v1._coords)
                al = approximateLength(offset)
                if al != 0 and al < v1._radius + v2._radius - 1: # Add orthogonal transition to the fastest one
                        if (approximateLength(v1._speed) >= approximateLength(v2._speed)):
                            v1._coords = vecAdd((v1._speed[1], -v1._speed[0]), v1._coords)
                        else :
                            v2._coords = vecAdd((-v2._speed[1], v2._speed[0]), v2._coords)

    def updatePositions(self):
        for v in self._vehicules:
            v._speed = vecAdd(v._speed, v._force)
            l = approximateLength(v._speed)
            if l > v._maxspeed:
                v._speed = vecScalarMult(v._speed, v._maxspeed / l)
            v._coords= (v._coords[0]+int(v._speed[0]), v._coords[1]+int(v._speed[1]))

    def neighboursBehaviour(self): #try to group vehicules
        for i, v1 in enumerate(self._vehicules):
            for v2 in self._vehicules[i + 1:]:
                offset = vecDiff(v2._coords, v1._coords)
                al = approximateLength(offset)
                # If you don't have any leader, set your max speed to his one if he is bigger
                if al != 0 and al < v1._radius + v2._radius + 2:
                    if(v1._radius < v2._radius and v1._leader == 0) :
                        v1._leader = v2
                        v1._maxspeed = v2._maxspeed
                    elif(v2._radius < v1._radius and v2._leader == 0) :
                        v2._leader = v2
                        v2._maxspeed = v1._maxspeed

                #If you lose your leader (too far) reset your max speed.
                if al != 0 and al >= (v1._radius + v2._radius) * 2:
                    if(v1._leader == v2) :
                        Vehicule.setDefaultMaxSpeed(v1)
                    elif(v2._leader == v1) :
                        Vehicule.setDefaultMaxSpeed(v2)

                #If you go beetwen two vehicules, update the leader
                if al != 0 and al < v1._radius + v2._radius + 2:
                    if(v1._radius < v2._radius and v1._leader != 0 and v1._leader == v2._leader) :
                        v1._maxspeed = v2._maxspeed
                        v1._leader = v2
                    elif(v2._radius < v1._radius and v2._leader != 0 and v1._leader == v2._leader) :
                        v2._maxspeed = v1._maxspeed * 1
                        v2._leader = v1

                #If you are ahead of your leader slowdown
                if al != 0 and al < v1._radius + v2._radius + 2:
                    if(v1._radius < v2._radius and v1._leader != 0) :
                        if (approximateLength(vecDiff(v1._coords, vecDiff(v1._coords, v2._speed))) <
                                approximateLength(vecDiff(v1._coords, vecDiff(v2._coords, v2._speed)))) :
                            v1._maxspeed = v2._maxspeed * 0.95
                        else :
                            v1._maxspeed = v2._maxspeed * 1
                    elif(v2._radius < v1._radius and v2._leader != 0) :
                        if (approximateLength(vecDiff(v1._coords, vecDiff(v1._coords, v1._speed))) >
                                approximateLength(vecDiff(v1._coords, vecDiff(v2._coords, v1._speed)))) :
                            v2._maxspeed = v1._maxspeed * 0.95
                        else :
                            v2._maxspeed = v1._maxspeed * 1



    def append(self,item):
        self._vehicules.append(item)

    def drawMe(self, screen, scene = None):
        for v in self._vehicules: v.drawMe(screen)


class Track:
    _circuit = None
    _cback = (128,128,128)
    _cfore = (10,10,10)
    _width = 30
    _screen = None
    _cachedLength = []
    _cachedNormals = []

    def __init__(self, screen):
        self._circuit = __circuit__
        self._screen = screen
        for i in range(0,len(self._circuit)):
            self._cachedNormals.append(vecDiff(self._circuit[i], self._circuit[len(self._circuit)-1 if i-1 < 0 else i-1]))
            self._cachedLength.append(approximateLength(self._cachedNormals[i]))
            self._cachedNormals[i] = (self._cachedNormals[i][0]/self._cachedLength[i], self._cachedNormals[i][1]/self._cachedLength[i])


    def _segmentPointAddLength(self, segment, point, length):
        ''' get the segment and point (on it) after adding length to the segment and point (on it), by following the
        path'''
        nextStep = approximateDistance(point, self._circuit[segment])
        if nextStep > length: # We stay on the same segment
            nextPoint = vecAdd(point, vecScalarMult(self._cachedNormals[segment], length))
            return (segment, (int(nextPoint[0]), int(nextPoint[1])))
        length -= nextStep
        segment = segment+1 if segment+1<len(self._circuit) else 0
        while length > self._cachedLength[segment]:
            length -= self._cachedLength[segment]
            segment = segment+1 if segment+1<len(self._circuit) else 0
        nextPoint = vecAdd(self._circuit[segment-1 if segment > 0 else len(self._circuit)-1],
                vecScalarMult(self._cachedNormals[segment], length))
        return (segment, (int(nextPoint[0]), int(nextPoint[1])))

    def _closestSegmentPointToPoint(self,point):
        bestLength = None
        bestPoint = None
        bestSegment = None
        for i in range(0, len(self._circuit)):
            p = self._closestPointToSegment(i,point)
            l = approximateDistance(p,point)
            if bestLength is None or l < bestLength:
                bestLength = l
                bestPoint = p
                bestSegment = i
        return (bestSegment, bestPoint, bestLength)

    def _closestPointToSegment(self, numSegment, point):
        ''' Returns the closest point on the circuit segment from point'''
        p0 = self._circuit[len(self._circuit)-1 if numSegment-1 < 0 else numSegment-1]
        p1 = self._circuit[numSegment]
        local = vecDiff(point, p0)
        projection = vecDot(local, self._cachedNormals[numSegment])
        if projection < 0:
            return p0
        if projection > self._cachedLength[numSegment]:
            return p1
        return vecAdd(p0,vecScalarMult(self._cachedNormals[numSegment], projection))

    def drawMe(self, scene = None):

        for p in self._circuit: # Draw simple inner joins
            pygame.draw.circle(self._screen,self._cback,p,int(self._width/2),0)
        pygame.draw.lines(self._screen, self._cback, True, self._circuit, self._width)
        pygame.draw.lines(self._screen, self._cfore, True, self._circuit, 1)

        if True:
            for i,p in enumerate(self._circuit):
                pygame.draw.line(self._screen, (0,0,250), p, vecAdd(p,vecScalarMult(self._cachedNormals[i], 50)))

        # if scene is not None:
        #     for i,p in enumerate(self._circuit):
        #         scene.drawText(str(int(self._cachedLength[i])), p)

class Scene:
    _track= None
    _vehicules = None
    _screen = None
    _font = None

    _mouseCoords = (0,0)

    def __init__(self, screenSize = __screenSize__):
        pygame.init()
        self._screen = pygame.display.set_mode(screenSize)
        self._track = Track(self._screen)
        self._vehicules = SetOfVehicules()
        #self._font = pygame.font.SysFont('Arial', 25)

    def drawMe(self):
        self._screen.fill((0,0,0))
        self._track.drawMe(scene = self)
        self._vehicules.drawMe(self._screen, scene = self)

        # Illustrate the closestSegmentPointToPoint function
        (s,p,l) = self._track._closestSegmentPointToPoint(self._mouseCoords)
        pygame.draw.line(self._screen, (128,255,128),p, self._mouseCoords)
        #print(self._track._segmentPointAddLength(s,p,150))
        pygame.draw.circle(self._screen, (128,255,128),self._track._segmentPointAddLength(s,p,150)[1],20,1)

        pygame.display.flip()

    def drawText(self, text, position, color = (255,128,128)):
        self._screen.blit(self._font.render(text,1,color),position)

    def update(self):
        for v in self._vehicules._vehicules:
            v.steerUpdate(self._track, self._vehicules)
        self._vehicules.updatePositions()
        self._vehicules.neighboursBehaviour()
        self._vehicules.handleCollisions()
        self.drawMe()

    def eventClic(self,coord,b):
        print("Adding Vehicule at ",coord[0],",",coord[1])
        self._vehicules.append(Vehicule((coord[0],coord[1])))


    def recordMouseMove(self, coord):
        self._mouseCoords = coord

def main():
    scene = Scene()
    done = False
    clock = pygame.time.Clock()
    while done == False:
        clock.tick(20)
        scene.update()
        scene.drawMe()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: done=True
            if event.type == pygame.KEYDOWN: done=True
            if event.type == pygame.MOUSEBUTTONDOWN:
                scene.eventClic(event.dict['pos'],event.dict['button'])
            elif event.type == pygame.MOUSEMOTION:
                scene.recordMouseMove(event.dict['pos'])

    pygame.quit()

if not sys.flags.interactive: main()

