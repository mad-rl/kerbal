import krpc
import json


class Telemetry(object):
    def __init__(
        self,
        o_apoapsis_altitude: float,
        o_periapsis_altitude: float,
        f_mean_altitude: float,
        crew_count: int,
        heading: float,
        pitch: float,
        roll: float,
        velocity: float,
        ut: float
    ):
        self.o_apoapsis_altitude = o_apoapsis_altitude
        self.o_periapsis_altitude = o_periapsis_altitude
        self.f_mean_altitude = f_mean_altitude
        self.crew_count = crew_count
        self.heading = heading
        self.pitch = pitch
        self.roll = roll
        self.velocity = velocity
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
        self.vessel = self.conn.space_center.active_vessel

    def reset_controls(self):
        self.vessel.control.sas = False
        self.vessel.control.rcs = False
        self.vessel.control.pitch = 0
        self.vessel.control.yaw = 0
        self.vessel.control.roll = 0

    def load_game(self, saved_game_name: str):
        try:
            self.conn.space_center.load(saved_game_name)
        except Exception as ex:
            print("Error:", ex)
            exit(
                f"You have no quick save named {saved_game_name}. Terminating.")

    def get_telemetry(self) -> Telemetry:
        sc = self.conn.space_center
        avo = self.vessel.orbit
        avf = self.vessel.flight()

        return Telemetry(
            self.conn.add_stream(getattr, avo, 'apoapsis_altitude')(),
            self.conn.add_stream(getattr, avo, 'periapsis_altitude')(),
            self.conn.add_stream(getattr, avf, 'mean_altitude')(),
            self.conn.add_stream(getattr, self.vessel, 'crew_count'),
            self.conn.add_stream(getattr, avf, 'heading'),
            self.conn.add_stream(getattr, avf, 'pitch'),
            self.conn.add_stream(getattr, avf, 'roll'),
            self.conn.add_stream(getattr, avf, 'velocity'),
            self.conn.add_stream(getattr, sc, 'ut')()
        )
