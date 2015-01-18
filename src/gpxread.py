from xml.dom import minidom

class GPXRead:

    points = None

    def __init__(self):
        """

        :rtype : None
        """
        self.points = []

    def read_points(self):

        xml_data_file = "/Users/isidro/Desktop/mine/tmp_track/activity_161545981.gpx"
        xml_data_file_content = open(xml_data_file, "rb").read()

        xml_data = minidom.parseString(xml_data_file_content)

        item_list = xml_data.getElementsByTagName('trkpt')

        for item in item_list:
            lat = item.attributes["lat"].value
            lon = item.attributes["lon"].value
            self.points.append({"lat": lat, "lon": lon})

        return self.points

    def get_starting_point(self):
        """
        :rtype : dict
        """

        return self.points[0]


if __name__ == "__main__":

    gpx_read = GPXRead()
    gpx_read.read_points()
