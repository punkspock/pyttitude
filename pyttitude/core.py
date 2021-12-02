from util import Point, Vector


class Pyttitude:
    def __init__(self, pos: Point, z_face: Vector, reference: Point = Point(0, 0, 0)):
        self.pos = pos
        self.z_face = z_face
        self.reference = reference

    def update(self, pos: Point = None, face: Vector = None):
        """
        :param Point pos: The updated position of the satellite
        :param Vector face: The updated face of the satellite
        """
        if pos is not None:
            self.pos = pos
        if face is not None:
            self.z_face = face

    @property
    def direction(self) -> Vector:
        """
        Get the directions that the satellite needs to be facing
        :return:
        """
        return Vector(
            self.reference.x - self.pos.x,
            self.reference.y - self.pos.y,
            self.reference.z - self.pos.z
        )

    def get_adjustments(self) -> Vector:
        """
        Get the angle between the +Z body axis of the satellite
        and the Earth vector (vector from satellite to Earth)
        :return:
        """
        return Vector(
            self.z_face.x - self.direction.x,
            self.z_face.y - self.direction.y,
            self.z_face.z - self.direction.z
        )
