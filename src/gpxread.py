from xml.dom import minidom
import globalmaptiles
import math
import datetime


class GPXPoint:
    def __init__(self, lat, lon, time=None):
        self.lat = lat
        self.lon = lon
        self.time = time

    def get_lat(self):
        return self.lat

    def get_lon(self):
        return self.lon

    def set_lat(self, lat):
        self.lat = lat

    def set_lon(self, lon):
        self.lon = lon


class GPXRead:
    points = None
    mercator = None

    def __init__(self):
        self.points = []
        self.mercator = globalmaptiles.GlobalMercator()

    def read_points(self):

        xml_data_file = "/Users/isidro/Desktop/mine/tmp_track/activity_37192771.gpx"
        xml_data_file = "/Users/isidro/Downloads/ubi-casa.gpx"
        xml_data_file = "c://Users//Leonardo//workspace//gpxtool//data/RK_gpx _2014-12-31_1732.gpx"
        xml_data_file_content = open(xml_data_file, "rb").read()

        xml_data = minidom.parseString(xml_data_file_content)

        item_list = xml_data.getElementsByTagName('trkpt')

        for item in item_list:
            lat = float(item.attributes["lat"].value)
            lon = float(item.attributes["lon"].value)
            time = None
            try:
                #time = datetime.datetime.strptime(item.getElementsByTagName('time')[0].childNodes[0].data, "%Y-%m-%dT%H:%M:%S.%fZ")
                time = datetime.datetime.strptime(item.getElementsByTagName('time')[0].childNodes[0].data, "%Y-%m-%dT%H:%M:%SZ")
            except:
                pass
            print(time)
            self.points.append(GPXPoint(lat, lon, time))

        return self.points

    def get_starting_point(self) -> GPXPoint:

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

    def calculate_point_data(self, point):
        lat = self.points[point].get_lat()
        lon = self.points[point].get_lon()
        time = self.points[point].time

        index_point = point
        prev_point = index_point - 1

        point_time = datetime.timedelta(seconds=1)
        point_distance = 0

        if prev_point >= 0:
            last_lat = self.points[prev_point].get_lat()
            last_lon = self.points[prev_point].get_lon()
            last_time = self.points[prev_point].time

            point_distance = self.distance_on_unit_sphere(lat, lon, last_lat, last_lon)
            point_time = time - last_time

        if point_time.seconds == 0:
            point_time = datetime.timedelta(seconds=1)

        return point_time, point_distance

    def calculate_total_distance(self):

        point_distance = 0
        total_distance = 0

        point_time = 0
        total_time = datetime.timedelta(0)

        num_point = 1
        last_lat = None
        last_lon = None
        last_time = None
        point_time = datetime.timedelta(0)

        for point in self.points:
            lat = point.get_lat()
            lon = point.get_lon()
            time = point.time
            if last_lat:
                point_distance = self.distance_on_unit_sphere(lat, lon, last_lat, last_lon)

                if time and last_time:
                    point_time = time - last_time
                total_distance += point_distance
                total_time += point_time

            #print("Point #" + str(num_point) + " => acc:" + str(total_distance) + " this:" + str(point_distance) + " time: " + str(total_time))

            last_lat = lat
            last_lon = lon
            last_time = time

            num_point += 1

        #print("Total distance: " + str(total_distance))
        return total_distance


if __name__ == "__main__":
    gpx_read = GPXRead()
    gpx_read.read_points()
    gpx_read.calculate_total_distance()
