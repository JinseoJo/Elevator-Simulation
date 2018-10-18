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
from entities import Person, Elevator
from visualizer import Visualizer


class SimulationParameters:
    """Helper class containing relevant parameters for Simulation class
    === Representation Invariants ===
    num_iterations >= 0
    num_floors >= 2
    """
    num_iterations: int
    num_floors: int
    arrival_generator: algorithms.ArrivalGenerator
    moving_algorithm: algorithms.MovingAlgorithm

    def __init__(self, config: Dict[str, Any]) -> None:
        self.num_iterations = 0
        self.num_floors = config['num_floors']
        self.arrival_generator = config['arrival_generator']
        self.moving_algorithm = config['moving_algorithm']


class SimulationStatistics:
    """Helper class storing statistics for Simulation"""
    people_completed: List[Person]
    total_people: int

    def __init__(self) -> None:
        self.people_completed = []
        self.total_people = 0


class Simulation:
    """The main simulation class.

    === Attributes ===
    elevators: a list of the elevators in the simulation
    visualizer: the Pygame visualizer used to visualize this simulation
    visualize: True or False, indicates if simulation will be visualized
    waiting: a dictionary of people waiting for an elevator
             (keys are floor numbers, values are the list of waiting people)
    stats: refer to SimulationStatistics class
    parameters: refer to SimulationParameters class
    """
    elevators: List[Elevator]
    visualizer: Visualizer
    visualize: bool
    waiting: Dict[int, List[Person]]
    stats: SimulationStatistics
    parameters: SimulationParameters

    def __init__(self,
                 config: Dict[str, Any]) -> None:
        """Initialize a new simulation using the given configuration."""

        self.visualize = config['visualize']

        self.elevators = []
        for _ in range(config['num_elevators']):
            e = Elevator(config['elevator_capacity'])
            self.elevators.append(e)
        self.waiting = {}
        self.stats = SimulationStatistics()
        self.parameters = SimulationParameters(config)

        # Initialize the visualizer.
        # Note that this should be called *after* the other attributes
        # have been initialized.
        self.visualizer = Visualizer(self.elevators,
                                     self.parameters.num_floors,
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
        self.parameters.num_iterations = num_rounds
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
            for floor in self.waiting:
                _update_wait_times(self.waiting[floor])
            for elevator in self.elevators:
                _update_wait_times(elevator.passengers)

            # Pause for 2 seconds
            self.visualizer.wait(2)

        return self._calculate_stats()

    def _generate_arrivals(self, round_num: int) -> None:
        """Generate and visualize new arrivals."""
        new_arrivals = self.parameters.arrival_generator.generate(round_num)
        for floor in new_arrivals:
            try:
                self.waiting[floor].extend(new_arrivals[floor])
            except KeyError:
                self.waiting[floor] = new_arrivals[floor]
            self.stats.total_people += len(new_arrivals[floor])
        if self.visualize:
            self.visualizer.show_arrivals(new_arrivals)

    def _handle_leaving(self) -> None:
        """Handle people leaving elevators."""

        for elevator in self.elevators:
            to_remove = []
            for person in elevator.passengers:
                if person.target == elevator.current_floor:
                    to_remove.append(True)
                    self.stats.people_completed.append(person)
                    if self.visualize:
                        self.visualizer.show_disembarking(person, elevator)
                else:
                    to_remove.append(False)
            new_list = [p for i, p in enumerate(elevator.passengers)
                        if not to_remove[i]]
            elevator.passengers = new_list[:]

    def _handle_boarding(self) -> None:
        """Handle boarding of people and visualize."""
        for i, elevator in enumerate(self.elevators):
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
                if self.visualize:
                    self.visualizer.show_boarding(person_to_board, elevator)
                num_people = len(elevator.passengers)

    def _move_elevators(self) -> None:
        """Move the elevators in this simulation.

        Use this simulation's moving algorithm to move the elevators.
        """
        directions = self.parameters.moving_algorithm.\
            move_elevators(self.elevators,
                           self.waiting,
                           self.parameters.num_floors)
        for index, elevator in enumerate(self.elevators):
            elevator.current_floor += directions[index].value
            print("elevator", index, "at floor", elevator.current_floor)

        if self.visualize:
            self.visualizer.show_elevator_moves(self.elevators, directions)

    ############################################################################
    # Statistics calculations
    ############################################################################
    def _calculate_stats(self) -> Dict[str, int]:
        """Report the statistics for the current run of this simulation.
        """
        num_iterations = self.parameters.num_iterations
        total_people = self.stats.total_people
        people_completed = len(self.stats.people_completed)
        wait_times = [p.wait_time for p in self.stats.people_completed]
        if not wait_times:
            max_time = -1
            min_time = -1
            avg_time = -1
        else:
            min_time = min(wait_times)
            max_time = max(wait_times)
            avg_time = int(sum(wait_times) / len(wait_times))

        return {
            'num_iterations': num_iterations,
            'total_people': total_people,
            'people_completed': people_completed,
            'max_time': max_time,
            'min_time': min_time,
            'avg_time': avg_time
        }


def _update_wait_times(people: List[Person]) -> None:
    """Updates the wait times for the list of Person objects"""
    if people:
        for person in people:
            person.wait_time += 1


def sample_run() -> Dict[str, int]:
    """Run a sample simulation, and return the simulation statistics."""
    config = {
        'num_floors': 6,
        'floor_height': 10,
        'num_elevators': 4,
        'elevator_capacity': 2,
        'num_people_per_round': 2,
        'arrival_generator': algorithms.FileArrivals(6, 'test3.csv'),
        'moving_algorithm': algorithms.ShortSighted(),
        'visualize': False
    }

    sim = Simulation(config)
    stats = sim.run(20)
    return stats


if __name__ == '__main__':
    # Uncomment this line to run our sample simulation (and print the
    # statistics generated by the simulation).
    sample_run()

    # import python_ta
    # python_ta.check_all(config={
    #     'extra-imports': ['entities', 'visualizer', 'algorithms', 'time'],
    #     'max-nested-blocks': 4
    # })
