import numpy as np

class Belief:

    def __init__(self):
        self.cars = []
        self.network = {}

    def addCars(self, car_ids):
        for i in car_ids:
            self.cars.append(i)

    def removeCars(self, car_ids):
        for i in car_ids:
            self.cars.remove(i)

    def hasCars(self):
        return len(self.cars) > 0
