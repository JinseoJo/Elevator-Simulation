"""CSC148 Assignment 1 - Simulation

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module description ===
This contains the main Simulation class that is actually responsible for
creating and running the simulation. You'll also find the function `sample_run`
here at the bottom of the file, which you can use as a starting point to run
your simulation on a small configuration.

Note that we have provided a fairly comprehensive list of attributes for
Simulation already. You may add your own *private* attributes, but should not
remove any of the existing attributes.
"""
# You may import more things from these modules (e.g., additional types from
# typing), but you may not import from any other modules.
from typing import Dict, List, Any

import algorithms
from algorithms import Direction
from entities import Person, Elevator
from visualizer import Visualizer


class Simulation:
    """The main simulation class.

    === Attributes ===
    arrival_generator: the algorithm used to generate new arrivals.
    elevators: a list of the elevators in the simulation
    moving_algorithm: the algorithm used to decide how to move elevators
    num_floors: the number of floors
    visualizer: the Pygame visualizer used to visualize this simulation
    waiting: a dictionary of people waiting for an elevator
             (keys are floor numbers, values are the list of waiting people)
    """
    arrival_generator: algorithms.ArrivalGenerator
    elevators: List[Elevator]
    moving_algorithm: algorithms.MovingAlgorithm
    num_floors: int
    visualizer: Visualizer
    waiting: Dict[int, List[Person]]
    num_iterations: int
    people_completed: List[Person]

    def __init__(self,
                 config: Dict[str, Any]) -> None:
        """Initialize a new simulation using the given configuration."""

        self.config = config
        self.num_floors = config['num_floors']

        self.elevators = []
        for _ in range(config['num_elevators']):
            e = Elevator(config['elevator_capacity'])
            self.elevators.append(e)

        self.arrival_generator = config['arrival_generator']
        self.moving_algorithm = config['moving_algorithm']

        self.waiting = {}
        self.num_iterations = 0
        self.people_completed = []

        # Initialize the visualizer.
        # Note that this should be called *after* the other attributes
        # have been initialized.
        self.visualizer = Visualizer(self.elevators,
                                     self.num_floors,
                                     config['visualize'])

    ############################################################################
    # Handle rounds of simulation.
    ############################################################################
    def run(self, num_rounds: int) -> Dict[str, Any]:
        """Run the simulation for the given number of rounds.

        Return a set of statistics for this simulation run, as specified in the
        assignment handout.

        Precondition: num_rounds >= 1.

        Note: each run of the simulation starts from the same initial state
        (no people, all elevators are empty and start at floor 1).
        """
        self.num_iterations = num_rounds
        for n in range(num_rounds):
            self.visualizer.render_header(n)

            # Stage 1: generate new arrivals
            self._generate_arrivals(n)

            # Stage 2: leave elevators
            self._handle_leaving()

            # Stage 3: board elevators
            self._handle_boarding()

            # Stage 4: move the elevators using the moving algorithm
            self._move_elevators()

            # Update wait times
            for floor in self.waiting.keys():
                self._update_wait_times(self.waiting[floor])
            for elevator in self.elevators:
                self._update_wait_times(elevator.passengers)

            # Pause for 1 second
            self.visualizer.wait(1)

        return self._calculate_stats()

    def _generate_arrivals(self, round_num: int) -> None:
        """Generate and visualize new arrivals."""
        new_arrivals = self.arrival_generator.generate(round_num)
        for floor in new_arrivals.keys():
            try:
                self.waiting[floor].extend(new_arrivals[floor])
            except KeyError:
                self.waiting[floor] = new_arrivals[floor]
        if self.config['visualize']:
            self.visualizer.show_arrivals(new_arrivals)

    def _handle_leaving(self) -> None:
        """Handle people leaving elevators."""

        for elevator in self.elevators:
            curr = elevator.passengers
            if curr:
                for person in curr:
                    target = person.target
                    if target == elevator.current_floor:
                        # print("target", person.target, "leaving at floor",
                        #       elevator.current_floor)
                        curr.remove(person)
                        self.people_completed.append(person)
                        if self.config['visualize']:
                            self.visualizer.show_disembarking(person, elevator)

    def _handle_boarding(self) -> None:
        """Handle boarding of people and visualize."""
        for elevator in self.elevators:
            num_people = len(elevator.passengers)
            floor = elevator.current_floor
            try:
                people_waiting = self.waiting[floor]
            except KeyError:
                continue
            while num_people < elevator.capacity and people_waiting:
                # pop(0) returns and removes the first person in waiting list
                person_to_board = people_waiting.pop(0)
                elevator.passengers.append(person_to_board)
                if self.config['visualize']:
                    self.visualizer.show_boarding(person_to_board, elevator)
                num_people = len(elevator.passengers)
            # print(elevator.passengers)

    def _move_elevators(self) -> None:
        """Move the elevators in this simulation.

        Use this simulation's moving algorithm to move the elevators.
        """
        directions = self.moving_algorithm.move_elevators(self.elevators,
                                                          self.waiting,
                                                          self.num_floors)
        print("directions: ", directions)
        for index, elevator in enumerate(self.elevators):
            elevator.current_floor += directions[index].value

        if self.config['visualize']:
            self.visualizer.show_elevator_moves(self.elevators, directions)

    def _update_wait_times(self, people: List[Person]) -> None:
        if people:
            for person in people:
                person.wait_time += 1

    ############################################################################
    # Statistics calculations
    ############################################################################
    def _calculate_stats(self) -> Dict[str, int]:
        """Report the statistics for the current run of this simulation.
        """
        num_iterations = self.num_iterations
        num_per_round = self.config['num_people_per_round']
        total_people = num_per_round * num_iterations
        people_completed = len(self.people_completed)
        wait_times = [person.wait_time for person in self.people_completed]
        min_time = min(wait_times)
        max_time = max(wait_times)
        avg_time = sum(wait_times) / len(wait_times)

        return {
            'num_iterations': num_iterations,
            'total_people': total_people,
            'people_completed': people_completed,
            'max_time': max_time,
            'min_time': min_time,
            'avg_time': avg_time
        }


def sample_run() -> Dict[str, int]:
    """Run a sample simulation, and return the simulation statistics."""
    config = {
        'num_floors': 6,
        'floor_height': 10,
        'num_elevators': 6,
        'elevator_capacity': 3,
        'num_people_per_round': 2,
        # Random arrival generator with 6 max floors and 2 arrivals per round.
        'arrival_generator': algorithms.RandomArrivals(6, 2),
        'moving_algorithm': algorithms.PushyPassenger(),
        'visualize': True
    }

    sim = Simulation(config)
    stats = sim.run(15)
    return stats


if __name__ == '__main__':
    # Uncomment this line to run our sample simulation (and print the
    # statistics generated by the simulation).
    print(sample_run())

    # import python_ta
    # python_ta.check_all(config={
    #     'extra-imports': ['entities', 'visualizer', 'algorithms', 'time'],
    #     'max-nested-blocks': 4
    # })
