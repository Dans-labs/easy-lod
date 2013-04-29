from rdflib import URIRef, Graph, Literal, Namespace
from oaipmh.client import Client
from oaipmh.metadata import MetadataRegistry, oai_dc_reader

registry = MetadataRegistry()
registry.registerReader('oai_dc', oai_dc_reader)
client = Client('http://easy.dans.knaw.nl/oai/', registry)
graph = Graph()
graph.namespace_manager.bind('dc11', 'http://purl.org/dc/elements/1.1/')
dc11 = Namespace('http://purl.org/dc/elements/1.1/')
failures = 0
for header, metadata, _ in client.listRecords(metadataPrefix='oai_dc'):
  try:
		s = URIRef(header.identifier())  # use oai header identifier as subject.
		for p, vv in metadata.getMap().iteritems():
			for v in vv:
				graph.add((s, dc11[p], Literal(v, lang = 'nl')))  # assume all values are Dutch literals. that's wrong.
	except Exception as e:
	 	failures += 1

graph.serialize('easy-lod.ttl', format='turtle')
print "Dump complete with {0} failures.".format(failures)
