# CAV
Connected Autonomous Vehicles (CAVs) Using Responsibility-Sensitive Safety (RSS) Rules

This repository intends to implement (mimic) the simulation of a new generalized algorithm for the cooperative driving of Connected Autonomous Vehicles (CAVs) in Python Language.

This is a part of the group project for the course CS637A (Embedded and Cyber-Physical Systems) taught by Dr. Indranil Saha at Indian Institute of Technology
Kanpur in the fall of 2021 (2021-22-1).

Original Paper: https://dl.acm.org/doi/10.1145/3450267.3450530

### HOW TO RUN

Open file "web/map.html" in your browser. Here there are many intuitive controls that will help you draw a graph. You may follow the "Notes" section below the main canvas to use this tool.

- Import a graph by pressing "I". Go to the file required, example "samples/square.json"
- Click "PLAY" button. It will communicate with Flask server (setup shown below). Simulation may take some time.
- Use the following commands to start server (recommended to use a virtual environment (vitualenv)):

```
$ git clone https://github.com/Ishanh2000/CAV
$ cd CAV
$ pip3 install virtualenv # assuming python3 and pip3 are installed
$ virtualenv venv
$ source venv/bin/activate # "deactivate" to deactivate vitual environment
$ pip3 install -U numpy flask flask-cors redis copy csv
$ export FLASK_APP=api
$ flask run --host=0.0.0.0
```

This had been a private repository till November 17, 2021. It has later been made public for visibility of the Instructor / Teaching Assistants.

### Video Demonstrations
The following video demonstrations may help you understand how the graphing tool works:
- [How to use the Graphing Tool]()
- [Demonstration of Cases]()

The files in "samples" folder are:
- **straight_1.json** : Straight road, one vehicle.
- **straight_2.json** : Straight road, two vehicles.
- **curve_1.json** : Curved road, one vehicle.
- **curve_2.json** : Curved road, two vehicles.
- **sharp_curve_1.json** : Sharply curved road, one vehicle.
- **sharp_curve_2.json** : Sharply curved road, two vehicles.
  - By manipulating code, the red vehicle speeds up near mid-point of path.
- **straight_2_block.json** : Straight road, two vehicles, but red vehicle is VERY slow.
- **square.json** : Multiple straight roads, four vehicles. Demonstrates Deadlock Resolution.

Other files in "samples" folder are experimental.

### Some Important Points
- When not playing the simulated path, the maximum speed of CAVs is mentioned.
- When playing the simulated path, the current speed of CAVs is mentioned.
- The ID of each CAV is displayed too.
- In the videos, the vehicles may seem to overlap on each other, but that is because they have been drawn larger. They actually do not collide.
- When a vehicle eaches its destination, it becomes "out of context", which is why other vehicles being blocked by it may speed up. Again. this does not mean the former vehicle is being trampled by others.


### Team Members
Contact the following if there is any issue:
- Anshul Rai (180117): anshulra@iitk.ac.in, anshulrai2001@gmail.com
- Ishanh Misra (180313): imisra@iitk.ac.in, ishanhmisra@gmail.com
- Utkarsh Gupta (180836): utkarshg@iitk.ac.in, utkarshg99@gmail.com
