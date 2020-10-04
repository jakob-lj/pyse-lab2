
import simpy
import numpy as np
import matplotlib.pyplot as plt
import string
import random

import sys

planes = []
iats = {}

P_DELAY = 0.5
MY_DELAY = 0/3600
T_LANDING = 1/60 # 60 seconds
T_TAKE_OFF = 1/60 # 60 seconds
MY_TA = 3/4

def getTime(time):
    return time % 24

def getHours(time):
    return "%s:%s" % (str(time).split('.')[0], int((time % 1)*60))

class PlaneGenerator(object):
    def __init__(self, env, runways):
        self.env = env
        self.runways = runways
        self.TGuard = 60/3600 # seconds
        self.PDelay = 0.5 # 

        env.process(self.generate())

        # Start the run process everytime an instance is created.
        # self.action = env.process(self.run())

    def generate(self):
        while True:
            if (getTime(self.env.now) >= 5): # generate no planes in this time period
                delay = self.getDelay()
                iat = self.interArrivalTime(getTime(self.env.now)) + delay
                plane = Plane(env, '%s' % self.env.now, iat, env.now, self.runways)
                # print(self.calcTimeout()._delay)
                yield env.timeout(iat + delay)
            else:
                yield self.env.timeout(5 - getTime(self.env.now))
        
    def getDelay(self):
        if (np.random.choice([True, False], p=[P_DELAY, 1- P_DELAY])):
            return self.getDelayTime()
        else:
            return 0

    def getDelayTime(self):
        return np.random.gamma(shape=3, scale = MY_DELAY)

    def calcTimeout(self):
        return env.timeout(self.interArrivalTime(getTime(self.env.now)))

    def interArrivalTime(self, time):
        # print("iat", self.Tned(time))
        return max(self.TGuard, self.Tned(time))

    def Tned(self, time):
        return self.TnedIntensity(time)/3600

    def TnedIntensity(self, time):
        timeOfDay = getTime(time)
        if (timeOfDay < 5):
            return None
        elif (timeOfDay < 8):
            return np.random.exponential(120)
        elif (timeOfDay < 11):
            return np.random.exponential(30)
        elif (timeOfDay < 15):
            return np.random.exponential(150)
        elif (timeOfDay < 20):
            return np.random.exponential(30)
        elif (timeOfDay < 24):
            return np.random.exponential(120)
        else:
            return None
        

class Plane(object):

    def __init__(self, env, name, iat, sced, runways):
        self.env = env
        #self.name = "%i" % int(float(name)*1000)
        self.name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(10)]).upper()
        self.interArrivalTime = iat
        self.scheduled = sced
        self.runways = runways
        self.env.process(self.live())
        planes.append(self)
        # print("Generated plane %.2f" % float(name))

    def getTurnAroundTime(self):
        return np.random.gamma(shape=7, scale=MY_TA)
        
    def live(self):
        with self.runways.request(priority=1) as req:
            yield req
            
            yield self.env.timeout(T_LANDING)
            print("Plane %s landed at %s" % (self.name, getHours(self.env.now)))
        
        tat = self.getTurnAroundTime()
        print("Plane %s requested airport facilities for %s hours with take off scheduled at %s" % (self.name, getHours(tat), getHours(self.env.now + tat)))
        yield self.env.timeout(tat)

        with self.runways.request(priority = 2) as req:
            yield req

            yield self.env.timeout(T_TAKE_OFF)
            print("Plane %s has left airspace at %s" % (self.name, getHours(self.env.now)))
    
        # while True:
        #     print('Start parking and charging at %d' % self.env.now)
        #     charge_duration = 5
        #     # We yield the process that process() returns
        #     # to wait for it to finish
        #     yield self.env.process(self.charge(charge_duration))

        #     # The charge process has finished and
        #     # we can start driving again.
        #     print('Start driving at %d' % self.env.now)
        #     trip_duration = 2
        #     yield self.env.timeout(trip_duration)

    # def charge(self, duration):
    #     yield self.env.timeout(duration)


env = simpy.Environment()
runways = simpy.PriorityResource(env, capacity=2)
pg = PlaneGenerator(env, runways)
env.run(until=24)

# means = np.zeros(24)

# for el in iats:
#     means[el] = iats[el]['sum'] / iats[el]['count']

# plt.plot(range(24), means)

print(len(planes))

n = len(planes)

x = [0, 5]
y = [0, 0]

m = 7
 
for i in range(0, n, m):
    y1 = y2 = y3 = 0
    x1 = x2 = x3 = 0

    xSum = 0
    ySum = 0
    nCalc = min(m, n - i)
    for j in range(nCalc):
        ySum += planes[i + j].interArrivalTime*3600 # convert to seconds
        xSum += planes[i + j].scheduled

    y.append(ySum/nCalc)
    x.append(xSum/nCalc)

plt.xlabel('Time of day')
plt.ylabel('IAT')

plt.title("MY_DELAY: %.0f seconds - P_DELAY: %s " % (MY_DELAY*3600, P_DELAY))

plt.plot(x, y)
plt.savefig('figs/my=%.0fp=%s.png' % (MY_DELAY*3600, P_DELAY))
plt.show()
