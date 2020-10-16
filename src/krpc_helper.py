from typing import Tuple, List
import krpc
import json
from settings import Settings


class Telemetry(object):
    def __init__(
        self,
        o_apoapsis_altitude: float,
        o_periapsis_altitude: float,
        f_mean_altitude: float,
        ut: float,
        crew_count: int,
        heading: float,
        pitch: float,
        roll: float,
        velocity: float
    ):
        self.o_apoapsis_altitude = o_apoapsis_altitude
        self.o_periapsis_altitude = o_periapsis_altitude
        self.f_mean_altitude = f_mean_altitude
        self.ut = ut
        self.crew_count = crew_count
        self.heading = heading
        self.pitch = pitch
        self.roll = roll
        self.velocity = velocity

    def json(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class KRPCHelper(object):
    def __init__(self, settings: Settings):
        conn_settings: dict = {
            "address": settings.krpc_address,
            "rpc_port": settings.krpc_rpc_port,
            "stream_port": settings.krpc_stream_port
        }
        self.settings: Settings = settings
        self.conn = krpc.connect(**conn_settings)
        self.vessel = self.conn.space_center.active_vessel

    def reset_controls(self):
        self.vessel.control.sas = False
        self.vessel.control.rcs = False
        self.vessel.control.pitch = 0
        self.vessel.control.yaw = 0
        self.vessel.control.roll = 0

    def load_game(self):
        try:
            self.conn.space_center.load(self.settings.save_game_name)
        except Exception as ex:
            print("Error:", ex)
            exit(f"You have no quick save named {self.settings.save_game_name}. Terminating.")

    def get_telemetry(self) -> Telemetry:
        sc = self.conn.space_center
        av = self.vessel
        avo = av.orbit
        avf = av.flight()
        avr = av.resources.all

        return Telemetry(
            self.conn.add_stream(getattr, avo, 'apoapsis_altitude')(),
            self.conn.add_stream(getattr, avo, 'periapsis_altitude')(),
            self.conn.add_stream(getattr, avf, 'mean_altitude')(),
            self.conn.add_stream(getattr, sc, 'ut')(),
            self.conn.add_stream(getattr, av, 'crew_count'),
            self.conn.add_stream(getattr, self.vessel.flight(), 'heading'),
            self.conn.add_stream(getattr, av.flight(), 'pitch'),
            self.conn.add_stream(getattr, av.flight(), 'roll'),
            self.conn.add_stream(getattr, av.flight(), 'velocity')
        )
