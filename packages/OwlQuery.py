from rdflib import Graph


class OwlQuery:

    def __init__(self, owl_path) -> None:
        self.g = Graph()
        self.g.parse(owl_path)

    def _parse(self, data: str) -> str:
        return data.split(":")[1].replace("_", " ")

    def get_process(self) -> list:

        res = self.g.query(
            'SELECT DISTINCT ?process ?clas WHERE {  ?clas rdfs:subClassOf    ?process .FILTER( STR(?clas) = "http://example.org/projet#process")} ORDER BY ?process')
        return [self._parse(i.process.n3(self.g.namespace_manager)) for i in res]

    def get_inp_tools_oup(self, process_name, data_type) -> list:
        data = data_type.replace(" ", "_")+"_"+process_name.replace(" ", "_")
        res = self.g.query(
            'SELECT DISTINCT ?input ?clas WHERE {  ?clas  rdf:type  ?input .FILTER( STR(?input) = "http://example.org/projet#'+data+'") }')
        return [self._parse(i.clas.n3(self.g.namespace_manager)).replace(data_type, "") for i in res]

    def _init_collection(self, id, collection_, is_dict=False):
        collection_[id] = collection_[
            id] if id in collection_.keys() else ({} if is_dict else [])
        return collection_

    def get_process_by_type(self, data_type):
        res = self.g.query(" SELECT DISTINCT ?type ?clas ?process   " +
                           " WHERE { ?clas  rdf:type   ?type." +
                           "FILTER contains( STR(?type) ,( \"http://example.org/projet#"+data_type+"_\"))" +
                           "}" +
                           "ORDER BY ?type")

        return [self._parse(i.clas.n3(self.g.namespace_manager)).replace(data_type, "") for i in res]

    def _get_other_info(self, data_type):
        data = []
        res = self.g.query("SELECT DISTINCT ?type ?clas ?process   " +
                           " WHERE { ?clas  rdfs:"+data_type+"   ?type." +
                           "}")
        for i in res:
            defi = self._parse(i.type.n3(self.g.namespace_manager)).split("#")
            data.append(
                (self._parse(i.clas.n3(self.g.namespace_manager)), defi[1] if len(defi) > 1 else defi[0]))
        return data

    def get_belong(self, instance):
        instance = instance.replace(" ", "_")

        res = self.g.query("SELECT DISTINCT ?p ?concept ?instance  " +
                           " WHERE { ?concept rdf:type  ?p." +
                           "?p rdfs:subClassOf  ?instance." +
                           "FILTER contains( STR(?concept) ,( \"http://example.org/projet#"+instance+"\"))" +
                           "}" +
                           "ORDER BY ?concept")
        return list(set([self._parse(i.instance.n3(self.g.namespace_manager)) for i in res]))

    def get_other_info(self):
        data = {}
        infos = self._get_other_info("isDefinedBy")
        infos.extend(self._get_other_info("seeAlso"))

        for word, defi in infos:
            data = self._init_collection(word, data)
            data[word].append(defi)

        return data

    def data(self, process_name):
        annotations = self.get_other_info()

        data = {pro: {} for pro in self.get_process()}
        for process, _ in data.items():
            for data_type in ["inputs", "tools_and_techniques", "outputs"]:
                data[process][data_type] = {
                    i: {} for i in self.get_inp_tools_oup(process, data_type)
                }

        for process, d in data.items():  # 1
            search = False
            if process_name == process:
                search = True
            if process in annotations.keys():
                data[process]["definition"] = " ".join(annotations[process])
            for data_type, values in d.items():  # 2
                if data_type == "definition":
                    continue
                for value, _ in values.items():  # 3
                    key = "Other informations"
                    data[process][data_type][value] = self._init_collection(
                        key, data[process][data_type][value])
                    if value in annotations.keys():
                        data[process][data_type][value][key].extend(
                            annotations[value])
                    if search:
                        key = f"{data_type} belong to"
                        data[process][data_type][value] = self._init_collection(
                            key, data[process][data_type][value])
                        data[process][data_type][value][key] = self.get_belong(
                            value)
                    for other_process, other_d in data.items():  # 1
                        if other_process != process:
                            for other_data_type, other_values in other_d.items():  # 2
                                if other_data_type in ["inputs", "tools_and_techniques", "outputs"] and value in other_values.keys():
                                    key = "Is "+other_data_type+" of these process"
                                    data[process][data_type][value] = self._init_collection(
                                        key, data[process][data_type][value])
                                    data[process][data_type][value][key].append(
                                        other_process)

        return data
