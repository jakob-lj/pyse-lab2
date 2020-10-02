
import simpy
import numpy as np
import matplotlib.pyplot as plt

import sys

planes = np.zeros(24)



def getTime(time):
    return time % 24

class PlaneGenerator(object):
    def __init__(self, env):
        self.env = env

        self.TGuard = 60/3600 # seconds
        self.PDelay = 0.5 # 
        self.XDelay = 0 # seconds

        env.process(self.generate())

        # Start the run process everytime an instance is created.
        # self.action = env.process(self.run())

    def generate(self):
        n = 0
        while n < 20000:
            if (getTime(self.env.now) >= 5): # generate no planes in this time period
                plane = Plane(env, '%s' % self.env.now)
                env.process(plane.run())
                # print(self.calcTimeout()._delay)
                yield self.calcTimeout()

            else:
                yield self.env.timeout(5 - getTime(self.env.now))
            n += 1
        
    def calcTimeout(self):
        return env.timeout(self.interArrivalTime(getTime(self.env.now)))

    def interArrivalTime(self, time):
        # print("iat", self.Tned(time))
        return max(self.TGuard, self.Tned(time))

    def Tned(self, time):
        return 1/self.TnedIntensity(time)

    def TnedIntensity(self, time):
        timeOfDay = getTime(time)
        if (timeOfDay < 5):
            return None
        elif (timeOfDay < 8):
            return 120/3
        elif (timeOfDay < 11):
            return 30/3
        elif (timeOfDay < 15):
            return 150/4
        elif (timeOfDay < 20):
            return 30/5
        elif (timeOfDay < 24):
            return 120/4
        else:
            return None
        

class Plane(object):

    def __init__(self, env, name):
        self.env = env
        self.name = name
        print("Generated plane %.2f" % float(name))
        planes[int(getTime(self.env.now))] += 1

    def run(self):
        while True:
            #print('Start parking and charging at %d' % self.env.now)
            charge_duration = 5
            # We may get interrupted while charging the battery

            # print('Start driving at %d' % self.env.now)
            trip_duration = 2
            yield self.env.timeout(trip_duration)

    
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
plane = PlaneGenerator(env)
env.run(until=24)

plt.xaxis()
plt.bar(np.linspace(0, 23, 24), planes)
plt.legend()
plt.show()