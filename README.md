# NEAT-Life prototype

Author: Ashley Leonard - psyal7

---

## Description

This is the simple prototype to the tool that applies the NEAT algorithm to Conway's Game of Life, 
that lets you run different experiments to try and find different patterns. Using the other main version 
would be better if you want to conduct proper larger scale experiments.

---

## Installation and Running

This project uses a few libraries for graphics, graphing and for the NEAT algorithm. Use the commands
below in a terminal or command prompt if you haven't already got them installed:

```
pip install pygame
```

```
pip install neat-python
```

```
pip install numpy
```

```
pip install matplotlib
```

---

## How to use the project

Part of the neat-python library is a [config file](neat_config.txt) which is explained 
[here](https://neat-python.readthedocs.io/en/latest/config_file.html) in the neat-python documentation.
An example for this can also be found 
[here](https://neat-python.readthedocs.io/en/latest/xor_example.html#example-source) (though this will 
just look similar to mine). Note that with the num_inputs parameter in this file should be NEAT_WIDTH * 
NEAT_HEIGHT + 2 (these variables can be found declared globally at the bottom of [main.py](main.py)).

You can change the dimensions of the board through the ROWS and COLUMNS variables at the top of
[board.py](board.py). Then the previously mentioned global variables NEAT_WIDTH and NEAT_HEIGHT give 
the size of the starting pattern area for the neural networks.


