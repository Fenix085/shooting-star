MAIN_LINE_TYPES = {"SEQUEL", "PREQUEL"}
IGNORE_TYPES = {"CHARACTER","OTHER", "ADAPTATION", "COMPILATION", "CONTAINS", "SAME_UNIVERSE"}
MAIN_LINE_DEPTH = 3
# BRANCH_DEPTH = 1

class RelationGraph():
    def __init__(self, client) -> None:
        self.client = client
        self.nodes: dict = {}
        self.edges: set = set()
        self.current = None

    def load_initial(self, start_id: int) -> None:
        self._expand_around(start_id)
        self.current = start_id

    def move_to(self, node_id: int) -> None:
        self.current = node_id
        self._expand_around(node_id)

    def _expand_around(self, start_id: int):

        self._fetch_and_merge(start_id)

        for r_type in MAIN_LINE_TYPES:
            current_level = [start_id]
            for _ in range(MAIN_LINE_DEPTH):
                new_level = []
                for entry in current_level:
                    self._fetch_and_merge(entry)
                    new_level.extend(self._find_next(entry, r_type))
                current_level = new_level    

    
            
    def _find_next(self, start_id: int, r_type: str) -> list[int]:
        found = []
        for edge in self.edges:
            if edge[0] == start_id and edge[2] == r_type:
                found.append(edge[1])
        return found
            

    def _fetch_and_merge(self, node_id: int) -> None:
        if node_id in self.nodes:
            if self.nodes[node_id]["expanded"] == True:
                return

        relations = self.client.get_relations(node_id)
        media = relations["Media"]
    
        self.nodes.setdefault(
            node_id,
            {
                "id": node_id,
                "title": media["title"],
                "format": media["format"],
                "episodes": media["episodes"],
                "year": media["seasonYear"],
                "expanded": False,
            }
        )

        self.nodes[node_id]["expanded"] = True

        for edge in media["relations"]["edges"]:
            e_node = edge["node"]
            source_id = node_id
            target_id = e_node["id"]
            relation_type = edge["relationType"]
            self.edges.add((source_id, target_id, relation_type))
            self.nodes.setdefault(
                target_id,
                {
                    "id": target_id,
                    "title": e_node["title"],
                    "format": e_node["format"],
                    "episodes": e_node["episodes"],
                    "year": e_node["seasonYear"],
                    "expanded": False,
                }
            )
        

    def frontier(self) -> list[int]:
        not_expanded = []
        for node in self.nodes.values():
            if node["expanded"] == False:
                not_expanded.append(node["id"])
        return not_expanded

