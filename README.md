##EASY Metadata as Linked Open Data Demo

### Motivation

- Generate an RDF dump of EASY metadata.
- Show off flexibility of SPARQL queries.
- Investigate issues related to publishing metadata as LOD.

### Status

This is a quick and dirty demo. Choices made are motivated by
the speed of implementation, nothing is guaranteed to work,
everything is likely to change.

### Implementation

OAI-PMH endpoint http://easy.dans.knaw.nl/oai/ is used without
authentication to harvest metadata and store it in n-triples format.

The metadata is expressed using DCMI Metadata Terms as in the original
dataset. Datasets are identified by OAI-PMH header identifier, and all
values are interpreted as Dutch literals.

See `dump.py` for details.

### Obtaining the Data

There are several ways to get the data. 

- Generate a new metadata dump run `python dump.py`.
- Download the dump from http://goo.gl/IOSmC
- Use the public SPARQL endpoint http://dydra.com/cgueret/easy-lod/sparql 

### Licence

TBC
