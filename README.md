# kerbal
DRL experiments with Kerbal Space Program

Based on Whiteaster solution:
https://medium.com/@whiteastercom/kerbal-space-program-complex-environment-for-reinforcement-learning-12318db065f5


Environment: Game + KRPC
https://krpc.github.io/krpc/


## KRPCHelper

This class allows the developer to detach the information on the game and the actual way to be used by a RL algorithm.

Example of using:
```python
from krpc_helper import KRPCHelper
kh = KRPCHelper()
tel = kh.get_telemetry()  # returns a Telemetry object with all the values filled with information in that moment
tel.json() # returns information in json format
```

Example of telemetry in json:
```json
{"o_apoapsis_altitude": 80.59333199064713, "o_periapsis_altitude": -598435.3256127913, "f_mean_altitude": 80.3575081480667, "f_g_force": 1.457995057106018, "f_velocity": [2.2400433021269194e-07, -0.005132530669624639, -3.669877963893751e-05], "f_speed": [0.0, 0.0, 0.0], "f_horizontal_speed": 0.0, "f_vertical_speed": 0.0, "f_center_of_mass": 0.0, "f_rotation": [0.0, 0.0, -0.0], "f_direction": [-0.4984657841294171, -0.4979526973247372, -0.5016898456216787, 0.5018787343241627], "f_normal": [0.9999996976658927, -0.00033041461197914337, -0.0007039135652466467], "f_anti_normal": [1.8900286717637993e-11, 0.9999999999947635, 3.2361967572235723e-06], "f_radial": [-2.2339202536414415e-11, -0.9999999999926816, -3.825831542297962e-06], "f_anti_radial": [0.9997535209880086, 9.828017941615128e-08, -0.02220128987402753], "f_atmosphere_density": [-0.9997416614959389, -1.145830762444653e-07, 0.022729062218377782], "f_dynamic_pressure": 1.1125531196594238, "f_static_pressure": 9.638421058654785, "f_aerodynamic_force": 100108.4453125, "f_drag": [-42.51984332902074, 0.008327416699266274, 0.10626491980332275], "f_lift": [-44.389176826348766, 0.014277106361063331, 0.10617604275047754], "r_resources": [{"name": "ElectricCharge", "amount": 150.0, "max": 150.0, "density": 0.0}, {"name": "MonoPropellant", "amount": 30.0, "max": 30.0, "density": 4.0}, {"name": "LiquidFuel", "amount": 2857.257080078125, "max": 2880.0, "density": 5.0}, {"name": "Oxidizer", "amount": 3490.38037109375, "max": 3520.0, "density": 5.0}, {"name": "SolidFuel", "amount": 426.1070556640625, "max": 433.0, "density": 7.5}, {"name": "SolidFuel", "amount": 425.6828918457031, "max": 433.0, "density": 7.5}, {"name": "SolidFuel", "amount": 425.25872802734375, "max": 433.0, "density": 7.5}, {"name": "SolidFuel", "amount": 424.83453369140625, "max": 433.0, "density": 7.5}, {"name": "ElectricCharge", "amount": 0.20000000298023224, "max": 0.20000000298023224, "density": 0.0}], "ut": 1894.6001068102037}
```

Telemetry class parameters: 
```python
    o_apoapsis_altitude: float,  # The apoapsis of the orbit, in meters, above the sea level of the body being orbited.
    o_periapsis_altitude: float,  # The periapsis of the orbit, in meters, above the sea level of the body being orbited.
    f_mean_altitude: float,  # The altitude above sea level, in meters. Measured from the center of mass of the vessel.
    f_g_force: float,  # The current G force acting on the vessel in g.
    f_velocity: Tuple[float, float, float],  # The velocity of the vessel, in the reference frame
    f_speed: float,  # The speed of the vessel in meters per second, in the reference frame ReferenceFrame.
    f_horizontal_speed: float,  # conn.add_stream(getattr, avf, 'aerodynamic_force'),
    f_vertical_speed: float,  # The speed of the vessel in meters per second, in the reference frame ReferenceFrame.
    f_center_of_mass:  Tuple[float, float, float],  # The position of the center of mass of the vessel, in the reference frame
    f_rotation: Tuple[float, float, float, float],  # The rotation of the vessel, in the reference frame
    f_direction: Tuple[float, float, float],  # The direction that the vessel is pointing in, in the reference frame
    f_normal: Tuple[float, float, float],  # The direction normal to the vessels orbit, in the reference frame
    f_anti_normal: Tuple[float, float, float],  # The direction opposite to the normal of the vessels orbit, in the reference frame
    f_radial: Tuple[float, float, float],  # The radial direction of the vessels orbit, in the reference frame
    f_anti_radial: Tuple[float, float, float],  # The direction opposite to the radial direction of the vessels orbit, in the reference frame
    f_atmosphere_density: float,  # The current density of the atmosphere around the vessel, in kg/m3.
    f_dynamic_pressure: float,  # The dynamic pressure acting on the vessel, in Pascals. This is a measure of the strength of the aerodynamic forces. It is equal to 12.air density.velocity2. It is commonly denoted Q.
    f_static_pressure: float,  # The static atmospheric pressure acting on the vessel, in Pascals.
    f_aerodynamic_force: Tuple[float, float, float],  # The total aerodynamic forces acting on the vessel, in reference frame
    f_drag: Tuple[float, float, float],  # The aerodynamic drag currently acting on the vessel.
    f_lift: Tuple[float, float, float],  # The aerodynamic lift currently acting on the vessel.
    r_resources: List[Resource],  # Represents the collection of resources stored in a vessel, stage or part.
    ut: float  # The current universal time in seconds.
```
