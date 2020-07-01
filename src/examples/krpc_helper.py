from typing import Tuple, List
import krpc
import json


class Resource(object):
    def __init__(
        self,
        name: str,  # The name of the resource.
        amount: float,  # The amount of the resource that is currently stored in the part.
        max: float,  # he total amount of the resource that can be stored in the part.
        density: float  # The density of the resource, in kg/l.
    ):
        self.name = name
        self.amount = amount
        self.max = max
        self.density = density


class Telemetry(object):
    def __init__(
        self,
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
    ):
        self.o_apoapsis_altitude = o_apoapsis_altitude
        self.o_periapsis_altitude = o_periapsis_altitude
        self.f_mean_altitude = f_mean_altitude
        self.f_g_force = f_g_force
        self.f_velocity = f_velocity
        self.f_speed = f_speed
        self.f_horizontal_speed = f_horizontal_speed
        self.f_vertical_speed = f_vertical_speed
        self.f_center_of_mass = f_center_of_mass
        self.f_rotation = f_rotation
        self.f_direction = f_direction
        self.f_normal = f_normal
        self.f_anti_normal = f_anti_normal
        self.f_radial = f_radial
        self.f_anti_radial = f_anti_radial
        self.f_atmosphere_density = f_atmosphere_density
        self.f_dynamic_pressure = f_dynamic_pressure
        self.f_static_pressure = f_static_pressure
        self.f_aerodynamic_force = f_aerodynamic_force
        self.f_drag = f_drag
        self.f_lift = f_lift
        self.r_resources = r_resources
        self.ut = ut

    def json(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class KRPCHelper(object):
    def __init__(self):
        conn_settings: dict = {
            "address": "127.0.0.1",
            "rpc_port": 50000,
            "stream_port": 50001
        }
        self.conn = krpc.connect(**conn_settings)

    def get_resources(self, avr: list) -> List[Resource]:
        resources: List[Resource] = []
        for r in avr:
            resources.append(Resource(
                self.conn.add_stream(getattr, r, 'name')(),
                self.conn.add_stream(getattr, r, 'amount')(),
                self.conn.add_stream(getattr, r, 'max')(),
                self.conn.add_stream(getattr, r, 'density')()
            ))
        return resources

    def get_telemetry(self) -> Telemetry:
        sc = self.conn.space_center
        av = sc.active_vessel
        avo = av.orbit
        avf = av.flight()
        avr = av.resources.all

        return Telemetry(
            self.conn.add_stream(getattr, avo, 'apoapsis_altitude')(),
            self.conn.add_stream(getattr, avo, 'periapsis_altitude')(),
            self.conn.add_stream(getattr, avf, 'mean_altitude')(),
            self.conn.add_stream(getattr, avf, 'g_force')(),
            self.conn.add_stream(getattr, avf, 'lift')(),
            self.conn.add_stream(getattr, avf, 'velocity')(),
            self.conn.add_stream(getattr, avf, 'speed')(),
            self.conn.add_stream(getattr, avf, 'horizontal_speed')(),
            self.conn.add_stream(getattr, avf, 'vertical_speed')(),
            self.conn.add_stream(getattr, avf, 'center_of_mass')(),
            self.conn.add_stream(getattr, avf, 'rotation')(),
            self.conn.add_stream(getattr, avf, 'direction')(),
            self.conn.add_stream(getattr, avf, 'normal')(),
            self.conn.add_stream(getattr, avf, 'anti_normal')(),
            self.conn.add_stream(getattr, avf, 'radial')(),
            self.conn.add_stream(getattr, avf, 'anti_radial')(),
            self.conn.add_stream(getattr, avf, 'atmosphere_density')(),
            self.conn.add_stream(getattr, avf, 'dynamic_pressure')(),
            self.conn.add_stream(getattr, avf, 'static_pressure')(),
            self.conn.add_stream(getattr, avf, 'aerodynamic_force')(),
            self.conn.add_stream(getattr, avf, 'drag')(),
            self.get_resources(avr),
            self.conn.add_stream(getattr, sc, 'ut')(),
        )
