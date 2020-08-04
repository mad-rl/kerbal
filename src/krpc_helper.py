from typing import Tuple, List
import krpc
import json
from settings import Settings


class Part(object):
    def __init__(
        self,
        name: str,
        axially_attached: bool,
        radially_attached: bool,
        stage: int,
        decouple_stage: int,
        mass: float,
        dry_mass: float,
        dynamic_pressure: float,
        temperature: float,
        skin_temperature: float,
        thermal_conduction_flux: float,
        thermal_convection_flux: float,
        thermal_radiation_flux: float,
        thermal_internal_flux: float
    ):
        self.name = name
        self.axially_attached = axially_attached
        self.radially_attached = radially_attached
        self.stage = stage
        self.decouple_stage = decouple_stage
        self.mass = mass
        self.dry_mass = dry_mass
        self.dynamic_pressure = dynamic_pressure
        self.temperature = temperature
        self.skin_temperature = skin_temperature
        self.thermal_conduction_flux = thermal_conduction_flux
        self.thermal_convection_flux = thermal_convection_flux
        self.thermal_radiation_flux = thermal_radiation_flux
        self.thermal_internal_flux = thermal_internal_flux


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
        f_g_force: float,
        f_rotation: Tuple[float, float, float, float],
        f_direction: Tuple[float, float, float],
        f_normal: Tuple[float, float, float],
        f_anti_normal: Tuple[float, float, float],
        f_radial: Tuple[float, float, float],
        f_anti_radial: Tuple[float, float, float],
        f_atmosphere_density: float,
        f_dynamic_pressure: float,
        f_static_pressure: float,
        f_aerodynamic_force: Tuple[float, float, float],
        f_drag: Tuple[float, float, float],
        f_lift: Tuple[float, float, float],
        r_resources: List[Resource],
        p_parts: List[Part],
        ut: float
    ):
        self.o_apoapsis_altitude = o_apoapsis_altitude
        self.o_periapsis_altitude = o_periapsis_altitude
        self.f_mean_altitude = f_mean_altitude
        self.f_g_force = f_g_force
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
        # self.p_parts = p_parts
        self.ut = ut

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

    def reset_controls(self):
        self.conn.space_center.active_vessel.control.sas = False
        self.conn.space_center.active_vessel.control.rcs = False
        self.conn.space_center.active_vessel.control.pitch = 0
        self.conn.space_center.active_vessel.control.yaw = 0
        self.conn.space_center.active_vessel.control.roll = 0
        self.conn.space_center.active_vessel.control.throttle = 0

    def load_game(self):
        self.conn.space_center.load(self.settings.save_game_name)

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

    def get_parts(self, avp: list) -> List[Part]:
        parts: List[Part] = []
        for p in avp:
            parts.append(Part(
                self.conn.add_stream(getattr, p, 'name')(),
                self.conn.add_stream(getattr, p, 'axially_attached')(),
                self.conn.add_stream(getattr, p, 'radially_attached')(),
                self.conn.add_stream(getattr, p, 'stage')(),
                self.conn.add_stream(getattr, p, 'decouple_stage')(),
                self.conn.add_stream(getattr, p, 'mass')(),
                self.conn.add_stream(getattr, p, 'dry_mass')(),
                self.conn.add_stream(getattr, p, 'dynamic_pressure')(),
                self.conn.add_stream(getattr, p, 'temperature')(),
                self.conn.add_stream(getattr, p, 'skin_temperature')(),
                self.conn.add_stream(getattr, p, 'thermal_conduction_flux')(),
                self.conn.add_stream(getattr, p, 'thermal_convection_flux')(),
                self.conn.add_stream(getattr, p, 'thermal_radiation_flux')(),
                self.conn.add_stream(getattr, p, 'thermal_internal_flux')()
            ))
        return parts
        
    def get_telemetry(self) -> Telemetry:
        sc = self.conn.space_center
        av = sc.active_vessel
        avo = av.orbit
        avf = av.flight()
        avr = av.resources.all
        avp = av.parts.all

        return Telemetry(
            self.conn.add_stream(getattr, avo, 'apoapsis_altitude')(),
            self.conn.add_stream(getattr, avo, 'periapsis_altitude')(),
            self.conn.add_stream(getattr, avf, 'mean_altitude')(),
            self.conn.add_stream(getattr, avf, 'g_force')(),
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
            self.conn.add_stream(getattr, avf, 'lift')(),
            self.get_resources(avr),
            self.get_parts(avp),
            self.conn.add_stream(getattr, sc, 'ut')(),
        )
