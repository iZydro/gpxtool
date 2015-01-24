from xml.dom import minidom
import globalmaptiles
import math


class GPXRead:
    points = None
    mercator = None

    def __init__(self):
        """

        :rtype : None
        """
        self.points = []
        self.mercator = globalmaptiles.GlobalMercator()

    def read_points(self):

        xml_data_file = "/Users/isidro/Desktop/mine/tmp_track/activity_161545981.gpx"
        xml_data_file_content = open(xml_data_file, "rb").read()

        xml_data = minidom.parseString(xml_data_file_content)

        item_list = xml_data.getElementsByTagName('trkpt')

        for item in item_list:
            lat = float(item.attributes["lat"].value)
            lon = float(item.attributes["lon"].value)
            self.points.append({"lat": lat, "lon": lon})

        return self.points

    def get_starting_point(self):
        """
        :rtype : dict
        """

        return self.points[0]

    def distance_on_unit_sphere(self, lat1, long1, lat2, long2):

        # Convert latitude and longitude to
        # spherical coordinates in radians.
        degrees_to_radians = math.pi / 180.0

        # phi = 90 - latitude
        phi1 = (90.0 - lat1) * degrees_to_radians
        phi2 = (90.0 - lat2) * degrees_to_radians

        # theta = longitude
        theta1 = long1 * degrees_to_radians
        theta2 = long2 * degrees_to_radians

        # Compute spherical distance from spherical coordinates.

        # For two locations in spherical coordinates
        # (1, theta, phi) and (1, theta, phi)
        # cosine( arc length ) =
        # sin phi sin phi' cos(theta-theta') + cos phi cos phi'
        # distance = rho * arc length

        cos = (math.sin(phi1) * math.sin(phi2) * math.cos(theta1 - theta2) +
               math.cos(phi1) * math.cos(phi2))
        arc = math.acos(cos)

        # Remember to multiply arc by the radius of the earth
        # in your favorite set of units to get length.
        return arc * 6378135.0

    def calculate_total_distance(self):

        total_distance = 0
        point_distance = 0
        num_point = 1
        last_lat = None
        last_lon = None

        for point in self.points:
            lat = float(point["lat"])
            lon = float(point["lon"])
            if last_lat:
                point_distance = self.distance_on_unit_sphere(lat, lon, last_lat, last_lon)
                # point_distance = (int(point_distance*10 + 0.5))/10.0
                total_distance += point_distance
            print("Point #" + str(num_point) + " => acc:" + str(total_distance) + " this:" + str(point_distance))
            last_lat = lat
            last_lon = lon
            num_point += 1
        print("Total distance: " + str(total_distance))
        return total_distance


if __name__ == "__main__":
    gpx_read = GPXRead()
    gpx_read.read_points()
    gpx_read.calculate_total_distance()
