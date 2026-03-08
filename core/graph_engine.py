import uuid

class Entity:
    def __init__(self, name, type, properties=None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.type = type # 'Domain', 'IP', 'Email', 'Alias', 'Organization'
        self.properties = properties or {}

class Relationship:
    def __init__(self, source_id, target_id, type):
        self.source_id = source_id
        self.target_id = target_id
        self.type = type # 'ResolvedTo', 'OwnedBy', 'MemberOf'

class GraphEngine:
    def __init__(self):
        self.entities = {}
        self.relationships = []

    def add_entity(self, name, type, properties=None):
        entity = Entity(name, type, properties)
        self.entities[entity.id] = entity
        return entity

    def add_relationship(self, source_id, target_id, type):
        rel = Relationship(source_id, target_id, type)
        self.relationships.append(rel)
        return rel

    def get_neighbors(self, entity_id):
        # Find all relationships where entity_id is source or target
        neighbors = []
        for rel in self.relationships:
            if rel.source_id == entity_id:
                neighbors.append((rel.target_id, rel.type, "OUT"))
            elif rel.target_id == entity_id:
                neighbors.append((rel.source_id, rel.type, "IN"))
        return neighbors

    def run_transform(self, entity_id, transform_name):
        entity = self.entities.get(entity_id)
        if not entity: return []
        
        new_entities = []
        # Mock transforms for now
        if transform_name == "DNS Resolve" and entity.type == "Domain":
            # In a real app, use socket.gethostbyname
            ip = "192.168.1." + str(hash(entity.name) % 255)
            e = self.add_entity(ip, "IP")
            self.add_relationship(entity_id, e.id, "ResolvesTo")
            new_entities.append(e)
            
        elif transform_name == "Whois Email" and entity.type == "Domain":
            email = "admin@" + entity.name
            e = self.add_entity(email, "Email")
            self.add_relationship(entity_id, e.id, "RegisteredWith")
            new_entities.append(e)

        return new_entities
