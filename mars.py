#!/usr/bin/python
__authour__ = 'darren.rael.everitt@gmail.com'


class RoverError(Exception):
    """
    Exception to be thrown if the instruction has moved the rover off
        the end of the plateu.
    :param: rover: Rover - so the catching code can make corrections.
    :param: instruction: the instruction letter.
    """
    def __init__(self, message, rover, instruction=''):

        # (Yes, I know I'm OCD about robustness.)
        if not isinstance(rover, Rover):
            raise ValueError(
                "EdgeOfGrid Exception: " +
                "'rover' ({rover}) must be of type Rover.".format(
                    rover
                )
            )

        # Parameter asignment
        self.rover = rover  # For extensibility in the error catching.
        self.message = """RoverError:
Rover '{}' at x={}, y={}, facing {} with instruction '{}'.
{}
        """.format(
            rover.name,
            rover.x,
            rover.y,
            rover.facing,
            instruction,
            message
        )


class Plateu:
    """
    This is the map of the playeu with rover objects on it I am using
    it to map where rovers are so as to avoid a collision.
    """
    def __init__(self, x_end, y_end, name="plateu"):

        # Parameter validation
        if (not isinstance(x_end, int)) and (x_end >= 0):
            raise ValueError(
                "Plateu: {} 'x_end' {} " +
                "must be a positive integer.".format(
                    name, x_end
                )
            )

        if (not isinstance(y_end, int)) and (y_end >= 0):
            raise ValueError(
                "Plateu: {} 'y_end' {} " +
                "must be a positive integer.".format(
                    name, y_end
                )
            )

        # Parameter Assignment
        self.name = name
        self.x_end = x_end
        self.y_end = y_end
        self.rovers = []  # A list of the rover objects on the map.


class Rover:
    """
    Instatiated as the object of a rover.
    :param: x, int - the x co-ordinate of the rover.
    :param: y, int - the y co-ordinate of the rover.
    :param: facing - one letter string indicating cardinal co-ordinate.
    """

    def __init__(self, x, y, facing, plateu, name):
        # Parameter validation
        if not isinstance(name, str):
            raise("Rover: 'name' ({}) must be a string.".format(name))

        if (not isinstance(x, int)) and (x >= 0):
            raise ValueError(
                "Rover: {} 'x' {}  must be a positive integer.".format(
                    name, x
                )
            )

        if (not isinstance(y, int)) and (y >= 0):
            raise ValueError(
                "Rover: {} 'y' {} must be a positive integer.".format(
                    name, y
                )
            )

        if (
            not isinstance(facing, str) and
            facing not in ['N', 'S', 'E', 'W']
        ):
            raise ValueError(
                "Rover: {} 'facing' {} must be " +
                "'N', 'S', 'E', or 'W'.".format(
                    name, facing
                )
            )

        if not isinstance(plateu, Plateu):
            raise ValueError(
                "Rover: {} 'plateu' {} must be of type Plateu".format(
                    name, plateu
                )
            )

        # Chack for (name, plateu) uniquenwss.
        for mr in plateu.rovers:
            if mr.name == name:
                raise ValueError("""Error:
Plateu already has a rover named '{}'
                """.format(
                        name
                    )
                )

        # Initialise porperties.
        self.name = name
        self.x = x
        self.y = y
        self.facing = facing
        self.plateu = plateu
        self.turn_left = {
            'N': 'W',
            'W': 'S',
            'S': 'E',
            'E': 'N'
        }
        self.turn_right = {v: k for k, v in self.turn_left.iteritems()}
        self.movement = {
            'N': {'axis': 'y', 'move': +1},
            'E': {'axis': 'x', 'move': +1},
            'S': {'axis': 'y', 'move': -1},
            'W': {'axis': 'x', 'move': -1}
        }

        self.position_rover('0')  # Run Error checking on rover position

    def get_position(self):

        return "{} {} {}".format(self.x, self.y, self.facing)

    def position_rover(self, instruction):

        # Check for valid instruction. (0 for initial position check)
        if instruction not in ['L', 'R', 'M', '0']:
            raise ValueError(
                "Rover: '{}'.position_rover instruction {} must be " +
                "'L', 'R', 'M', or '0'".format(
                    self.name,
                    instruction
                )
            )

        if instruction == 'L':

            self.facing = self.turn_left[self.facing]

        elif instruction == 'R':

            self.facing = self.turn_right[self.facing]

        else:

            facing = self.movement[self.facing]
            axis = facing['axis']
            axis_pos = getattr(self, axis)

            if instruction == 'M':
                axis_pos += facing['move']

            new_x = axis_pos if axis == 'x' else self.x
            new_y = axis_pos if axis == 'y' else self.y
            # Check that we're still on the grid:
            if (
                new_x > self.plateu.x_end or
                new_y > self.plateu.y_end or
                new_x < 0 or
                new_y < 0
            ):
                raise RoverError('On edge of grid.', self, instruction)

            # Check that we're not colliding with another rover:
            for mr in self.plateu.rovers:
                if mr != self and mr.x == new_x and mr.y == new_y:
                    raise RoverError(
                        "Would Collide with '{}'.".format(mr.name),
                        self,
                        instruction
                    )

            if instruction == '0':
                self.plateu.rovers.append(self)
            else:
                self.x = new_x
                self.y = new_y

        return self.get_position()

    def undo_move(self):
        # Extension to use to revert the rover's position.
        self.position_rover('R')
        self.position_rover('R')
        self.position_rover('M')


def process_rover(grid, start_at, instructions, name='rover'):
    """
    This function instantiates the above classes into objects.
    It is here called by __main__, it could be called by an API or CLI
    """
    plateu = None
    try:
        if isinstance(grid, str):
            x_end, y_end = grid.split(' ')
            x_end = int(x_end)
            y_end = int(y_end)
            plateu = Plateu(x_end, y_end, name)

        elif isinstance(grid, Plateu):
            plateu = grid

        else:
            raise ValueError("'grid' must be of type str or Plateu.")

    except Exception as e:
        # Error handling code here for plateu here.
        print(e.message)
        return e  # Should be re-raises and handled by API, CLI, etc.

    try:
        x, y, f = start_at.split(' ')
        x = int(x)
        y = int(y)
        rover = Rover(x, y, f, plateu, name)
        for i in range(len(instructions)):
            rover.position_rover(instructions[i])
            # Leaving this in comments for later debugging.
            # print(instructions[i] +
            # repr(rover.position_rover(instructions[i])))

    except Exception as e:
        # Error handling code here for rover here.
        print(e.message)
        return e  # Should be re-raises and handled by API, CLI, etc.

    print(rover.get_position())
    return rover


if __name__ == '__main__':

    rover1 = process_rover('5 5', '1 2 N', 'LMLMLMLMM', 'rover1')
    plateu = rover1.plateu

    # Test for name error:
    process_rover(plateu, '3 3 E', 'MMRMMRMRRM', 'rover1')

    rover2 = process_rover(plateu, '3 3 E', 'MMRMMRMRRM', 'rover2')

    # Test for collision error:
    rover3 = process_rover(plateu, '4 1 E', 'MMRML', 'rover3')

    # Test for edge of grid error:
    rover4 = process_rover(plateu, '0 1 S', 'MMRML', 'rover4')

    # We could add more rovers here

"""
>python mars.py
1 3 N
Error:
Plateu already has a rover named 'rover1'

5 1 E
RoverError:
Rover 'rover3' at x=4, y=1, facing E with instruction 'M'.
Would Collide with 'rover2'.

RoverError:
Rover 'rover4' at x=0, y=0, facing S with instruction 'M'.
On edge of grid.

"""
