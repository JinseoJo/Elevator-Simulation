"""CSC148 Assignment 1 - People and Elevators

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module description ===
This module contains classes for the two "basic" entities in this simulation:
people and elevators. We have provided basic outlines of these two classes
for you; you are responsible for implementing these two classes so that they
work with the rest of the simulation.

You may NOT change any existing attributes, or the interface for any public
methods we have provided. However, you can (and should) add new attributes,
and of course you'll have to implement the methods we've provided, as well
as add your own methods to complete this assignment.

Finally, note that Person and Elevator each inherit from a kind of sprite found
in sprites.py; this is to enable their instances to be visualized properly.
You may not change sprites.py, but are responsible for reading the documentation
to understand these classes, as well as the abstract methods your classes must
implement.
"""
from __future__ import annotations
from typing import List
from sprites import PersonSprite, ElevatorSprite


class Elevator(ElevatorSprite):
    """An elevator in the elevator simulation.

    === Attributes ===
    passengers: A list of the people currently on this elevator; the later
        passengers are appended, so the order from earliest to latest boarding
        is read from left to right
    current_floor: An int describing the floor the elevator is on
    capacity: the maximum number of people possible

    === Representation invariants ===
    current_floor > 0
    capacity > 0
    """
    passengers: List[Person]
    current_floor: int
    capacity: int

    def __init__(self, capacity: int):
        ElevatorSprite.__init__(self)
        self.passengers = []
        self.current_floor = 1
        self.capacity = capacity

    def fullness(self) -> float:
        """Return the fraction that this elevator is filled.

           The value returned should be a float between 0.0 (completely empty) and
           1.0 (completely full).
        """
        return float(len(self.passengers) / self.capacity)


ANGER_LEVELS = {0:0, 1:0, 2:0, 3:1, 4:1, 5:2, 6:2, 7:3, 8:3}


class Person(PersonSprite):
    """A person in the elevator simulation.

    === Attributes ===
    start: the floor this person started on
    target: the floor this person wants to go to
    wait_time: the number of rounds this person has been waiting

    === Representation invariants ===
    start >= 1
    target >= 1
    wait_time >= 0
    """
    start: int
    target: int
    wait_time: int

    def __init__(self, start: int, target: int, wait_time: int):
        PersonSprite.__init__(self)
        self.start = start
        self.target = target
        self.wait_time = 0


    def get_anger_level(self) -> int:
        """Return this person's anger level.

        A person's anger level is based on how long they have been waiting
        before reaching their target floor.
            - Level 0: waiting 0-2 rounds
            - Level 1: waiting 3-4 rounds
            - Level 2: waiting 5-6 rounds
            - Level 3: waiting 7-8 rounds
            - Level 4: waiting >= 9 rounds
        """
        return ANGER_LEVELS.get(self.wait_time, 4)  # 4 is the default value


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['sprites'],
        'max-nested-blocks': 4
    })
