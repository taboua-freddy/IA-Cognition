from rdflib import Graph, URIRef
from rdflib.namespace import RDFS, SKOS, OWL, RDF, XSD


g = Graph()

g.parse("onto1.owl")

# 'SELECT DISTINCT ?process ?clas WHERE {  ?clas rdfs:subClassOf    ?process .FILTER( STR(?clas) = "http://example.org/projet#process")} ORDER BY ?process')
qres0 = g.query("SELECT DISTINCT ?p ?concept ?instance  " +
                " WHERE { ?concept rdf:type  ?p." +
                "?p rdfs:subClassOf  ?instance." +
                "FILTER contains( STR(?concept) ,( \"http://example.org/projet#project_documents_updates\"))" +
                "}" +
                "ORDER BY ?concept"
                )
for i in qres0:
    print(i.p.n3(g.namespace_manager) +
          "------>"+i.concept.n3(g.namespace_manager) +
          "------>"+i.instance.n3(g.namespace_manager))
