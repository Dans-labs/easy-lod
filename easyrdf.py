import itertools
import re
import os
import rdflib
from datetime import datetime
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
        s = easy_url(header.identifier())
        graph = rdflib.Graph(identifier=s)
        metadata_fields = metadata.getMap().iteritems()
        for p, vv in metadata_fields:
            for v in vv:
                graph.add((s, dc11[p], rdflib.Literal(v)))
        yield graph

def oai_metadata(oai_endpoint, from_datetime=None):
    registry = MetadataRegistry()
    registry.registerReader('oai_dc', oai_dc_reader)
    client = Client(oai_endpoint, registry)
    return make_graphs(client.listRecords(metadataPrefix='oai_dc', from_=from_datetime))

def add_geo(graph):
    for s, o in graph.subject_objects(dc11.coverage):
        coord = re.findall(u'\u03c6\u03bb=([\d.]+\s[\d.]+);\sprojection=http://www.opengis.net/def/crs/EPSG/0/4326;', o)
        if coord:
            wkt_point = "point({0})".format(coord[0])
            graph.add((s, geo.geometry, rdflib.Literal(wkt_point, datatype=virtrdf.Geometry)))
    return graph

def easy_rdf(max_records=None, from_datetime=None):
    """
    Returns an iterator over rdflib.Graph objects each representing metadata of a single EASY dataset.
    """
    easy_records = itertools.islice(oai_metadata(EASY_OAI, from_datetime=from_datetime  ), max_records)
    return itertools.imap(add_geo, easy_records)

def update_query(graph, graph_name, delete_subject=None):
    ntriples = graph.serialize(format='nt')
    if delete_subject:
        delete_block = '''DELETE WHERE {{GRAPH <{0}> {{ <{1}> ?p ?v }} }};\n'''.format(graph_name, delete_subject)
    else:
        delete_block = ''
    insert_clause = '''INSERT DATA {{ GRAPH <{0}> {{ {1} }} }}\n'''.format(graph_name, ntriples)
    return delete_block + insert_clause 

def update_triplestore(records, sparql_endpoint_uri=EASY_SPARQL, graph_name=EASY_TARGET_GRAPH, clean_type='none'):
    """
    Save records to triplestore.

    clean_type must be one of the following:
    'all'           - DROP graph graph_name before update
    'incremental'   - DELETE triples with subject matching record identifier
    'none'          - do not try to delete outdated triples

    :param records: iterable of rdflib.Graph objects
    :param sparql_endpoint_uri: SPARQL Update endpoint
    :type sparql_endpoint_uri: str
    :param graph_name: target graph name
    :type graph_name: str
    """
    target_graph = rdflib.Graph(store='SPARQLUpdateStore', identifier=graph_name)
    target_graph.open((sparql_endpoint_uri, sparql_endpoint_uri), create=False)
    delete_subject_getter = lambda: None
    if clean_type == 'all':
        target_graph.update('''DROP SILENT GRAPH <{}>'''.format(graph_name))
    elif clean_type == 'incremental':
        delete_subject_getter = lambda: record.identifier
    elif clean_type and (clean_type != 'none'):
        raise ValueError("clean_type parameter must be 'all', 'incremental', or 'none'")
    for record in records:
        target_graph.update(update_query(record, graph_name, delete_subject=record.identifier))

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

def test():
    for c in ['all', 'incremental', 'none']:
        update_triplestore(easy_rdf(max_records=30), clean_type=c)
        print c

def test_last():
    dump_nt(easy_rdf(from_datetime=datetime(2014, 5, 15)), 'test_last2.nt')

if __name__ == '__main__':
    dump_nt(easy_rdf(), 'easy.nt')
