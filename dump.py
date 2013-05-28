from rdflib import URIRef, Graph, Literal, Namespace
from oaipmh.client import Client
from oaipmh.metadata import MetadataRegistry, oai_dc_reader

easy_id = Namespace('https://easy.dans.knaw.nl/ui/datasets/id/easy-dataset:')

def easy_url(oai_id):
	namespace, dataset = oai_id.rsplit(':', 1)
	if namespace != 'oai:easy.dans.knaw.nl:easy-dataset':
		raise(Exception("Unknown namespace: {0}".format(namespace)))
	return easy_id[dataset]

registry = MetadataRegistry()
registry.registerReader('oai_dc', oai_dc_reader)
client = Client('http://easy.dans.knaw.nl/oai/', registry)
graph = Graph()
graph.namespace_manager.bind('dc11', 'http://purl.org/dc/elements/1.1/')
dc11 = Namespace('http://purl.org/dc/elements/1.1/')
# max_count = 30000
for count, (header, metadata, _) in enumerate(client.listRecords(metadataPrefix='oai_dc')):
	# if count >= max_count:
	# 	break
	if metadata is not None:
	    metadata_fields = metadata.getMap().iteritems()
		s = easy_url(header.identifier())
		for p, vv in metadata_fields:
			for v in vv:
				graph.add((s, dc11[p], Literal(v)))

graph.serialize('easy-lod.nt', format='nt')
