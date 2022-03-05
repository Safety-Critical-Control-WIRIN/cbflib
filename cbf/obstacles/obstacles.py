#!/bin/python3
"""

The Obstacle classes containing the neccessary gradients and hessian functions for
seamless integration with optimal solvers, includes several utility objects like 
the obstacle list for use in real time simulation.

author: Neelaksh Singh

"""

import numpy as np
from euclid import *
# import carla

import warnings
from collections.abc import MutableMapping
from cvxopt import matrix

# Identity Objects
DICT_EMPTY_UPDATE = ()

# Object Selectors for utility
ELLIPSE2D = 0

class Obstacle2DBase():
    """
    The base class each 2D obstacle class will inherit from. Created to enforce specific
    validation checks in the obstacle list objects and creating the neccessary interface
    for all 2D obstacle CBF classes.
    """
    def __init__(self):
        pass

    def evaluate(self, p):
        if not isinstance(p, Vector2):
            raise TypeError("Expected an object of type euclid.Vector2 for arg p, but got " + type(p).__name__ + ".")

    def gradient(self, p):
        if not isinstance(p, Vector2):
            raise TypeError("Expected an object of type euclid.Vector2 for arg p, but got " + type(p).__name__ + ".")
        return matrix(0.0, (3,1))

    def f(self, p):
        if not isinstance(p, Vector2):
            raise TypeError("Expected an object of type euclid.Vector2 for arg p, but got " + type(p).__name__ + ".")
        return 0
    
    def dx(self, p):
        if not isinstance(p, Vector2):
            raise TypeError("Expected an object of type euclid.Vector2 for arg p, but got " + type(p).__name__ + ".")
        return 0
    
    def dy(self, p):
        if not isinstance(p, Vector2):
            raise TypeError("Expected an object of type euclid.Vector2 for arg p, but got " + type(p).__name__ + ".")
        return 0

    def dtheta(self, p):
        if not isinstance(p, Vector2):
            raise TypeError("Expected an object of type euclid.Vector2 for arg p, but got " + type(p).__name__ + ".")
        return 0

    def update(self):
        pass

    def updateCoords(self, xy):
        if not isinstance(xy, Vector2):
            raise TypeError("Expected an object of type euclid.Vector2 for arg p, but got " + type(xy).__name__ + ".")
        pass

    def updateOrientation(self):
        pass

class Ellipse2D(Obstacle2DBase):
    def __init__(self, a, b, center = Vector2(0, 0), theta=0, buffer=0):
        """
        Generates the 2D Ellipse obstacle representation for use in control barrier functions.
        Exposes the required functionality for direct usage in CBF as a barrier constraint.

        """
        if not isinstance(center, Vector2):
            raise TypeError("Expected an object of type euclid.Vector2 for arg center, but got " + type(center).__name__ + ".")
        self.center = center
        self.theta = theta
        self.a = a + buffer
        self.b = b + buffer
        self.buffer = buffer
        self.BUFFER_FLAG = True
    
    def applyBuffer(self):
        if not self.BUFFER_FLAG:
            self.a = self.a + self.buffer
            self.b = self.b + self.buffer
            self.BUFFER_FLAG = True
        else:
            warnings.warn("Warning: Buffer already applied. Call Ignored.")
        
    def removeBuffer(self):
        if self.BUFFER_FLAG:
            self.a = self.a - self.buffer
            self.b = self.b - self.buffer
            self.BUFFER_FLAG = False
        else:
            warnings.warn("Warning: Buffer already removed. Call Ignored.")
    
    def evaluate(self, p):
        """
        Evaluate the value of the ellipse at a given point.
        """
        super().evaluate(p)
        dx = p.x - self.center.x
        dy = p.y - self.center.y
        ct = np.cos(self.theta)
        st = np.sin(self.theta)

        eval = ( ( dx * ct + dy * st )/self.a )**2 + ( ( -dx * st + dy * ct )/self.b )**2 - 1
        return eval

    def gradient(self, p):
        super().gradient(p)
        return matrix([self.dx(p), self.dy(p), self.dtheta(p)])

    # f = evaluate
        
    def f(self, p):
        """
        Alias of the evaluate function, semantically significant for cvxopt.
        """
        return self.evaluate(p)
    
    def dx(self, p):
        super().dx(p)
        xd = p.x - self.center.x
        yd = p.y - self.center.y
        ct = np.cos(self.theta)
        st = np.sin(self.theta)

        dx_ = (2 * ct/(self.a**2)) * ( xd * ct + yd * st ) + (-2 * st/(self.b**2)) * ( -xd * st + yd * ct )
        return dx_
    
    def dy(self, p):
        super().dy(p)
        xd = p.x - self.center.x
        yd = p.y - self.center.y
        ct = np.cos(self.theta)
        st = np.sin(self.theta)

        dy_ = (2 * st/(self.a**2)) * ( xd * ct + yd * st ) + (2 * ct/(self.b**2)) * ( -xd * st + yd * ct )
        return dy_
    
    def update(self, a=None, b=None, center=None, theta=None, buffer=None):
        if a is not None:
            self.a = a
        if b is not None:
            self.b = b
        if center is not None:
            if not isinstance(center, Vector2):
                raise TypeError("Expected an object of type euclid.Vector2 for arg center.")
            self.center = center
        if theta is not None:
            self.theta = theta
        if buffer is not None:
            if self.BUFFER_FLAG:
                self.a = self.a - self.buffer + buffer
                self.b = self.b - self.buffer + buffer
                self.buffer = buffer
            else:
                self.buffer = buffer
    
    def updateCoords(self, xy):
        super().updateCoords(xy)
        self.center = xy

    def updateOrientation(self, yaw):
        self.theta = yaw

    def updateByBoundingBox(self, BBox):
        a = BBox.extent.x
        b = BBox.extent.y
        center = Vector2(BBox.location.x, BBox.location.y)
        theta = BBox.rotation.yaw
        self.update(a=a, b=b, center=center, theta=theta)

    def dtheta(self, p):
        """
        Despite being zero. This function is still created for the sake of completeness w.r.t API.
        """
        return super().dtheta(p)

    def __repr__(self):
        return f"{type(self).__name__}(a = {self.a}, b = {self.b}, center = {self.center}, theta = {self.theta}, buffer = {self.buffer}, buffer applied: {self.BUFFER_FLAG} )\n"
    
    @classmethod
    def fromBoundingBox(cls, BBox, buffer = 0.5):
        if not isinstance(BBox, carla.BoundingBox):
            raise TypeError("Expected an object of type carla.BoundingBox as an input to fromCarlaBoundingBox() method, but got ", type(BBox).__name__)
        
        a = BBox.extent.x
        b = BBox.extent.y
        center = Vector2(BBox.location.x, BBox.location.y)
        theta = BBox.rotation.yaw
        return cls(a, b, center, theta, buffer)
        
class ObstacleList2D(MutableMapping):

    def __init__(self, data=()):
        self.mapping = {}
        self.update(data)
    
    def __getitem__(self, key):
        return self.mapping[key]
    
    def __delitem__(self, key):
        del self.mapping[key]
    
    def __setitem__(self, key, value):
        """
        Contaions the enforced base class check to ensure it contains
        an object derived from the 2D obstacle base class.
        """
        # Enforcing base class check using mro.
        if not Obstacle2DBase in value.__class__.__mro__:
            raise TypeError("Expected an object derived from Obstacle2DBase as value. Received " + type(value).__name__)
        self.mapping[key] = value

    def __iter__(self):
        return iter(self.mapping)

    def __len__(self):
        return len(self.mapping)
    
    def __repr__(self):
        return f"{type(self).__name__}({self.mapping})"

    def updateByBoundingBox(self, obs_dict=None, obs_type=ELLIPSE2D, buffer=0.5):
        """
        Will update the obstacle based on the dynamic obstacle
        list criteria. Remove the IDs which are not present in
        the scene and add those which entered the scene. Update
        the IDs which have changed locations for reformulation 
        of the contained obstacle objects.
        """
        if obs_dict is not None:
            for key, bbox in obs_dict.items():
                if key in self.mapping.keys():
                    self.mapping[key].updateByBoundingBox(bbox)
                else:
                    if obs_type == ELLIPSE2D:
                        self.__setitem__(key, Ellipse2D.fromBoundingBox(bbox, buffer))
            for key in self.mapping.keys():
                if key not in obs_dict.keys():
                    self.pop(key)

    def f(self, p):
        f = matrix(0.0, (len(self.mapping), 1))
        idx = 0
        for obs in self.mapping.values():
            f[idx] = obs.f(p)
            idx = idx + 1
        return f

    def dx(self, p):
        dx = matrix(0.0, (len(self.mapping), 1))
        idx = 0
        for obs in self.mapping.values():
            dx[idx] = obs.dx(p)
            idx = idx + 1
        return dx

    def dy(self, p):
        dy = matrix(0.0, (len(self.mapping), 1))
        idx = 0
        for obs in self.mapping.values():
            dy[idx] = obs.dy(p)
            idx = idx + 1
        return dy
    
    def dtheta(self, p):
        dtheta = matrix(0.0, (len(self.mapping), 1))
        idx = 0
        for obs in self.mapping.values():
            dtheta[idx] = obs.dtheta(p)
            idx = idx + 1
        return dtheta

    def gradient(self, p):
        df = matrix(0.0, (len(self.mapping), 3))
        idx = 0
        for obs in self.mapping.values():
            df[idx,:] = obs.gradient(p).T
            idx = idx + 1
        return df