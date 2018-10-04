"""CSC148 Assignment 1 - Algorithms

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module Description ===

This file contains two sets of algorithms: ones for generating new arrivals to
the simulation, and ones for making decisions about how elevators should move.

As with other files, you may not change any of the public behaviour (attributes,
methods) given in the starter code, but you can definitely add new attributes
and methods to complete your work here.

See the 'Arrival generation algorithms' and 'Elevator moving algorithsm'
sections of the assignment handout for a complete description of each algorithm
you are expected to implement in this file.
"""
import csv
from enum import Enum
import random
from typing import Dict, List, Optional

from entities import Person, Elevator


###############################################################################
# Arrival generation algorithms
###############################################################################
class ArrivalGenerator:
    """An algorithm for specifying arrivals at each round of the simulation.

    === Attributes ===
    max_floor: The maximum floor number for the building.
               Generated people should not have a starting or target floor
               beyond this floor.
    num_people: The number of people to generate, or None if this is left
                up to the algorithm itself.

    === Representation Invariants ===
    max_floor >= 2
    num_people is None or num_people >= 0
    """
    max_floor: int
    num_people: Optional[int]

    def __init__(self, max_floor: int, num_people: Optional[int]) -> None:
        """Initialize a new ArrivalGenerator.

        Preconditions:
            max_floor >= 2
            num_people is None or num_people >= 0
        """
        self.max_floor = max_floor
        self.num_people = num_people

    def generate(self, round_num: int) -> Dict[int, List[Person]]:
        """Return the new arrivals for the simulation at the given round.

        The returned dictionary maps floor number to the people who
        arrived starting at that floor.

        You can choose whether to include floors where no people arrived.
        """
        raise NotImplementedError


class RandomArrivals(ArrivalGenerator):
    """Generate a fixed number of random people each round.

    Generate 0 people if self.num_people is None.

    For our testing purposes, this class *must* have the same initializer header
    as ArrivalGenerator. So if you choose to to override the initializer, make
    sure to keep the header the same!

    Hint: look up the 'sample' function from random.
    """
    pass


class FileArrivals(ArrivalGenerator):
    """Generate arrivals from a CSV file.
    """
    def __init__(self, max_floor: int, filename: str) -> None:
        """Initialize a new FileArrivals algorithm from the given file.

        The num_people attribute of every FileArrivals instance is set to None,
        since the number of arrivals depends on the given file.

        Precondition:
            <filename> refers to a valid CSV file, following the specified
            format and restrictions from the assignment handout.
        """
        ArrivalGenerator.__init__(self, max_floor, None)

        # We've provided some of the "reading from csv files" boilerplate code
        # for you to help you get started.
        with open(filename) as csvfile:
            reader = csv.reader(csvfile)
            for line in reader:
                # TODO: complete this. <line> is a list of strings corresponding
                # to one line of the original file.
                # You'll need to convert the strings to ints and then process
                # and store them.
                pass


###############################################################################
# Elevator moving algorithms
###############################################################################
class Direction(Enum):
    """
    The following defines the possible directions an elevator can move.
    This is output by the simulation's algorithms.

    The possible values you'll use in your Python code are:
        Direction.UP, Direction.DOWN, Direction.STAY
    """
    UP = 1
    STAY = 0
    DOWN = -1


class MovingAlgorithm:
    """An algorithm to make decisions for moving an elevator at each round.
    """
    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        """Return a list of directions for each elevator to move to.

        As input, this method receives the list of elevators in the simulation,
        a dictionary mapping floor number to a list of people waiting on
        that floor, and the maximum floor number in the simulation.

        Note that each returned direction should be valid:
            - An elevator at Floor 1 cannot move down.
            - An elevator at the top floor cannot move up.
        """
        raise NotImplementedError

    def no_one_waiting(self, waiting: Dict[int, List[Person]]) -> bool:
        """ A helper function for the moving algorithms

        Returns True if no one is waiting, False otherwise
        """
        for floor in waiting.keys():
            if waiting[floor]:
                return False
        return True

    def get_direction(self, target, current) -> Direction:
        """ A helper function for the moving algorithms

        Returns the direction of travel for a given current position and target
        """
        if target < current:
            return Direction.DOWN
        elif target == current:
            return Direction.STAY
        else:
            return Direction.UP


class RandomAlgorithm(MovingAlgorithm):
    """A moving algorithm that picks a random direction for each elevator.
    Returns a list of Directions
    """
    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        directions = []
        choices = [Direction.UP, Direction.DOWN, Direction.STAY]
        for e in elevators:
            valid = False
            while not valid:
                r = random.sample(choices, k=1)
                potential_floor = e.current_floor + r[0].value
                if 0 < potential_floor <= max_floor:
                    directions.append(r[0])
                    valid = True
        return directions


class PushyPassenger(MovingAlgorithm):
    """A moving algorithm that preferences the first passenger on each elevator.

    If the elevator is empty, it moves towards the *lowest* floor that has at
    least one person waiting, or stays still if there are no people waiting.

    If the elevator isn't empty, it moves towards the target floor of the
    *first* passenger who boarded the elevator.
    """
    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        directions = []
        for e in elevators:
            num_people = len(e.passengers)
            if num_people == 0 and self.no_one_waiting(waiting):
                directions.append(Direction.STAY)
            elif num_people == 0:
                directions.append(self._move_to_lowest_waiting(waiting, e))
            else:
                first_passenger = e.passengers[0]
                destination = first_passenger.target
                directions.append(self.get_direction(destination, e.current_floor))
        return directions

    def _move_to_lowest_waiting(self, waiting: Dict[int, List[Person]],
                                e: Elevator) -> Direction:
        """ Moves to the lowest floor that has at least one person waiting
            Returns the direction of elevator movement
            Precondition: there is at least one person waiting in the building
        """
        lowest_floor = 0
        for floor in sorted(waiting.keys()):
            if waiting[floor]:
                lowest_floor = floor
                break
        assert lowest_floor > 0, "Error in private method: lowest waiting"
        return self.get_direction(lowest_floor, e.current_floor)


class ShortSighted(MovingAlgorithm):
    """A moving algorithm that preferences the closest possible choice.

    If the elevator is empty, it moves towards the *closest* floor that has at
    least one person waiting, or stays still if there are no people waiting.

    If the elevator isn't empty, it moves towards the closest target floor of
    all passengers who are on the elevator.

    In this case, the order in which people boarded does *not* matter.
    """
    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        directions = []
        for e in elevators:
            num_people = len(e.passengers)
            if num_people == 0 and self.no_one_waiting(waiting):
                directions.append(Direction.STAY)
            elif num_people == 0:
                direction = self.move_to_closest_waiting(waiting, max_floor, e)
                directions.append(direction)
            else:
                target_floors = [passenger.target for passenger in e.passengers]
                curr = e.current_floor
                gap = 1
                found = False
                while not found:
                    # search the bottom
                    if curr-gap in target_floors:
                        directions.append(Direction.DOWN)
                        found = True
                    # search the top
                    elif curr+gap in target_floors:
                        directions.append(Direction.UP)
                        found = True
                    gap += 1
        return directions

    def move_to_closest_waiting(self, waiting: Dict[int, List[Person]],
                                e: Elevator) -> Direction:
        """ Moves to the closest floor that has at least one person waiting
        This is called only when there's at least one person waiting in the
        building
        Returns the direction of movement

        """
        curr = e.current_floor
        gap = 1
        while True:
            # search the bottom
            try:
                if waiting[curr-gap]:
                    return Direction.DOWN
            except KeyError:
                pass
            # search the top
            try:
                if waiting[curr+gap]:
                    return Direction.UP
            except KeyError:
                pass
            gap += 1


if __name__ == '__main__':
    # Don't forget to check your work regularly with python_ta!
    import python_ta
    python_ta.check_all(config={
        'allowed-io': ['__init__'],
        'extra-imports': ['entities', 'random', 'csv', 'enum'],
        'max-nested-blocks': 4,
        'disable': ['R0201']
    })
