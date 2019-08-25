
Hardware considerations
=======================

Some things are not necessarily obvious when you look at a suspended bot for the first time. Here are a few heads-up:

1. **Slack cables**. If you have more than 3 cables, you may have at least one "slack cable": one that is not necessary for the platform to maintain its position. It may, however, play a role in the orientation of the plaform. In the presence of a slack cable, the final orientation of the platform will depend on the weight repartition of the charge of the platform.

2. **Orientation**. Obvious now but at first I had not realized that the orientation of the platform depends on the XYZ position and that it can't be assumed to be flat everywhere. Hightly constrained systems, like 8-wires bots with 4 wires pulling downwards can force an orientation everywhere, but that's not our case.

3. **Steppers are not servos**. I think choosing steppers for this prototype was a mistake. Steppers are the common choice for CNCs but in our case, they have some undesirable properties:

  3.1. **Constant current**. They consume a constant current whatever the load is. They will always move with the maximum strength. It means that unlike with DC motors, you can't measure their current to gauge the load.

  3.2. **Missed steps**. Steppers are great because they have very precise and reliable step sizes, but if the load exceeds their capabilities, they will miss steps silently.

  3.3 **Power hungry**. The motors will consume a lot of current even when static. Making this project energy-efficient is a much longer term objective, but it is good to know that as it is now, it would drain a lot of batttery power just for staying in a static position.

  3.4 **Vibrations**. Because they are designed to move by steps, movements of steppers are irregular and will cause a lot of vibrations. The system needs to be prepared for it.

4. **Winding**. The art of winding a wire around a bobbin is harder than it seems (than it seemed to me at least).

  4.1 **Spool diameter**. The spool diameter determines the amount of wire wcah motor increment will roll and the strength the system can exert on the wires, determining its final liftable load. It is crucial. Thing is, the amount of wire rolled on the spool can change this diameter significantly. I first thought it was negligible if I had a big enough spool. It turns out that any decent length of wire will stack up quickly on a small bobbin, especially when considering the next paragraph

  4.2 **Winding is irregular**. Depending on the angle the wire arrives on the spool, you may have all the wire stack on one side, an almost regular winding or a bump in the middle. I am not sure if this is a thing that solve with a good angle alone. After all, in places where regular winding is crucial (maritime cables for instance) there is a motorized feeder that moves to place the wire at the correct spot on the spool. I hope we can do without.

  4.3 **Winding depends on tension**. A slack cable will roll in a loose way whereas a cable under tension will roll tightly, possibly with a slightly mall diameter.
