
Robot Control & Machine Learning
================================

In theory, the math to control that machine is not that hard. For the position you want to reach, you compute the length the cables should have. You need to take into account the size of the platform and the angle it will be at but that's doable.

You just need a model able to tell you what the wire length should be for each position. A realistic model, however, will have a lot of parameters:
- XYZ positions of the winches
- size of the platform
- load
- elasticity of wires
- bend of the poles the winches are placed on
- variation of the effective diameter of the spools as wires roll on them

Writing that model is not the hardest part, the hardest one is to design a calibration procedure that is realistic given the deployements constraints. My objective is to get a robot that can be deployed in a random field, by planting poles a bit approximately. For this scenario, the calibration procedure is everything.

So here is how the calibration procedure would typically go for such a robot: Have a ground truth, in this case the pose of an ART marker placed on the platform, and run a scripted or random sequence of motor orders, then try to adjust the parameters of the model so that it manages to predict the platform pose from the motors positions.

Thing is, such a model is likely to be non-linear, so it will require some sort of optimization technique, quite possibly a gradient descent. It would also probably benefit from manual tuning of parameters, not all being equally important.

So I wondered, why not replace this calibration step by a deep learning model? This seems like a perfect problem for it.


Predictions or policies?
------------------------

There are two ways to approach this problem: One may be tempted to use reinforcement learning to directly make the model produce the motors outputs. Looking into the litterature about it, there are some models training a model to produce analog output policies, but they are experimental right now.

The other approach, that I explored more, is to create a predictive model of the platform's pose according to the motors commands issued. Then, with this model, it is easy to make an iterative search algorithm find motors orders that would lead to a desired movement.

The inputs for such a model is the current position and the current commands sent to motors. It seems recommended to also feed in the previous position and previous motor command. We will need to investigate several time steps, I experimented with 5 poses per second for now.
