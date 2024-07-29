import json

from perp_simulation.entity.simulation import Simulation


class SimulationSerializer:
    """Serialize simulation data to JSON format."""

    @staticmethod
    def to_json(simulation: Simulation) -> str:
        """Serialize simulation."""
        return json.dumps(simulation.to_dict())
