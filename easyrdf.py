import itertools
import re
import os
import rdflib
from oaipmh.client import Client
from oaipmh.metadata import MetadataRegistry, oai_dc_reader

EASY_OAI = 'http://easy.dans.knaw.nl/oai/'
EASY_SPARQL = 'http://localhost:8890/sparql'
EASY_TARGET_GRAPH = 'https://easy.dans.knaw.nl'

dc11 = rdflib.Namespace('http://purl.org/dc/elements/1.1/')
geo = rdflib.Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')
virtrdf = rdflib.Namespace('http://www.openlinksw.com/schemas/virtrdf#')
easy_id = rdflib.Namespace('https://easy.dans.knaw.nl/ui/datasets/id/easy-dataset:')

def easy_url(oai_id):
    namespace, dataset = oai_id.rsplit(':', 1)
    if namespace != 'oai:easy.dans.knaw.nl:easy-dataset':
        raise(Exception("Unknown namespace: {0}".format(namespace)))
    return easy_id[dataset]

def make_graphs(oai_records):
    for header, metadata, _ in oai_records:
        if metadata is None:
            continue
        graph = rdflib.Graph()
        s = easy_url(header.identifier())
        metadata_fields = metadata.getMap().iteritems()
        for p, vv in metadata_fields:
            for v in vv:
                graph.add((s, dc11[p], rdflib.Literal(v)))
        yield graph

def oai_metadata(oai_endpoint):
    registry = MetadataRegistry()
    registry.registerReader('oai_dc', oai_dc_reader)
    client = Client(oai_endpoint, registry)
    return make_graphs(client.listRecords(metadataPrefix='oai_dc'))

def add_geo(graph):
    for s, o in graph.subject_objects(dc11.coverage):
        coord = re.findall(u'\u03c6\u03bb=([\d.]+\s[\d.]+);\sprojection=http://www.opengis.net/def/crs/EPSG/0/4326;', o)
        if coord:
            wkt_point = "point({0})".format(coord[0])
            graph.add((s, geo.geometry, rdflib.Literal(wkt_point, datatype=virtrdf.Geometry)))
    return graph

def easy_rdf(max_records=None):
    easy_records = itertools.islice(oai_metadata(EASY_OAI), max_records)
    return itertools.imap(add_geo, easy_records)

def update_query(graph, graph_name):
    ntriples = graph.serialize(format='turtle')
    return '''INSERT DATA {{ GRAPH <{0}> {{ {1} }} }}'''.format(graph_name, ntriples)

def update_triplestore(records, sparql_endpoint_uri=EASY_SPARQL, graph_name=EASY_TARGET_GRAPH):
    """
    Save records to triplestore

    :param records: iterable of rdflib.Graph objects
    :param sparql_endpoint_uri: SPARQL Update endpoint
    :type sparql_endpoint_uri: str
    :param graph_name: target graph name
    :type graph_name: str
    """
    target_graph = rdflib.Graph(store='SPARQLUpdateStore', identifier=graph_name)
    target_graph.open((sparql_endpoint_uri, sparql_endpoint_uri), create=False)
    for record in records:
        target_graph.update(update_query(record, graph_name))

def dump_nt(records, filename, mode='w'):
    """
    Save records to disk in N-Triples format

    :param records: iterable of rdflib.Graph objects
    :param filename: output file name
    :param mode: file open mode
    """
    fout = open(filename, mode)
    for record in records:
        record.serialize(fout, format='nt')

if __name__ == '__main__':
    dump_nt(easy_rdf(), 'easy.nt')
