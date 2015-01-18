from xml.dom import minidom


def read_points():

    xml_data_file = "/Users/isidro/Desktop/mine/tmp_track/activity_161545981.gpx"
    xml_data_file_content = open(xml_data_file, "rb").read()

    xml_data = minidom.parseString(xml_data_file_content)

    item_list = xml_data.getElementsByTagName('trkpt')

    points = []

    for item in item_list:
        lat = item.attributes["lat"].value
        lon = item.attributes["lon"].value
        print ("lat:" + lat + " - lon:" + lon)
        points.append({"lat": lat, "lon": lon})

    return points

if __name__ == "__main__":

    read_points()
