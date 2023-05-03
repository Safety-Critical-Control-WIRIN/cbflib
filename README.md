# cbflib
Release of the CBF library to apply the cone CBFs described in the paper:

P. Thontepu et al., Control Barrier Functions in UGVs for Kinematic Obstacle Avoidance: A Collision Cone Approach. arXiv, 2022. doi: 10.48550/ARXIV.2209.11524.

This library allows for an easy interface for creating collision cones out of 3D bounding boxes and when given an interface to the state feedback from the vehicle, handles all of the computation for the collision cone CBF (C3BF) allowing for moving obstacle avoidance with theoretical guarantees on safety. The output of the C3BF processing functions is a continuous, real-time, and optimal modification of the reference control input which ensures collision avoidance. 
***
Therefore, the library provides a minimally invasive safety filter for the reference control inputs, which can, in theory, be generated through any algortihm. Using C3BFs adds a layer of safety and continuity to the control input, since the resulting final control input will be Lipshitz Continuous.
***
