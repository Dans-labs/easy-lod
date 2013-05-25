import re
from rdflib import Graph, Namespace, Literal
g = Graph()
g2 = Graph()
g.parse('easy-lod.nt', format='nt')
dc11 = Namespace('http://purl.org/dc/elements/1.1/')
geo = Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')
virtrdf = Namespace('http://www.openlinksw.com/schemas/virtrdf#')
for s, p, o in g.triples((None, dc11.coverage, None)):
	coord = re.findall(u'\u03c6\u03bb=([\d.]+\s[\d.]+);\sprojection=http://www.opengis.net/def/crs/EPSG/0/4326;', o)
	if coord:
		wkt_point = "point({0})".format(coord[0])
		g2.add((s, geo.geometry, Literal(wkt_point, datatype=virtrdf.Geometry)))
g2.serialize('easy-geo.nt', format='nt')
