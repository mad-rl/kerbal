import krpc
import json


class Resource(object):
    def __init__(
        self,
        name: str,
        amount: float,
        max: float,
        density: float
    ):
        self.name = name
        self.amount = amount
        self.max = max
        self.density = density


class Telemetry(object):
    def __init__(
        self,
        o_apoapsis_altitude: float,
        o_periapsis_altitude: float,
        f_mean_altitude: float,
        f_surface_altitude: float,
        f_g_force: float,
        f_orbital_speed: float,
        f_surface_speed: float,
        f_latitude: float,
        f_longitude: float,
        ut: float
    ):
        self.o_apoapsis_altitude = o_apoapsis_altitude
        self.o_periapsis_altitude = o_periapsis_altitude
        self.f_mean_altitude = f_mean_altitude
        self.f_surface_altitude = f_surface_altitude
        self.f_g_force = f_g_force
        self.f_orbital_speed = f_orbital_speed
        self.f_surface_speed = f_surface_speed
        self.f_latitude = f_latitude
        self.f_longitude = f_longitude
        self.ut = ut

    def json(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class KRPCHelper(object):
    def __init__(self, address: str, rpc_port: int, stream_port: int):
        conn_settings: dict = {
            "address": address,
            "rpc_port": rpc_port,
            "stream_port": stream_port
        }
        self.conn = krpc.connect(**conn_settings)

    def reset_controls(self):
        self.conn.space_center.active_vessel.control.sas = False
        self.conn.space_center.active_vessel.control.rcs = False
        self.conn.space_center.active_vessel.control.pitch = 0
        self.conn.space_center.active_vessel.control.yaw = 0
        self.conn.space_center.active_vessel.control.roll = 0
        self.conn.space_center.active_vessel.control.throttle = 0

    def load_game(self, saved_game_name: str):
        self.conn.space_center.load(saved_game_name)

    def get_telemetry(self) -> Telemetry:
        sc = self.conn.space_center
        av = sc.active_vessel
        avo = av.orbit
        avf = av.flight()
        av.position(av.orbital_reference_frame)
        av.position(av.surface_reference_frame)
        avo_frame = av.flight(av.orbit.body.non_rotating_reference_frame)
        avs_frame = av.flight(av.orbit.body.reference_frame)

        return Telemetry(
            self.conn.add_stream(getattr, avo, 'apoapsis_altitude')(),
            self.conn.add_stream(getattr, avo, 'periapsis_altitude')(),
            self.conn.add_stream(getattr, avf, 'mean_altitude')(),
            self.conn.add_stream(getattr, avf, 'surface_altitude')(),
            self.conn.add_stream(getattr, avf, 'g_force')(),
            self.conn.add_stream(getattr, avo_frame, 'speed')(),
            self.conn.add_stream(getattr, avs_frame, 'speed')(),
            self.conn.add_stream(getattr, avf, 'latitude')(),
            self.conn.add_stream(getattr, avf, 'longitude')(),
            self.conn.add_stream(getattr, sc, 'ut')(),
        )
