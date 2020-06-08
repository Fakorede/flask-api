from ma import ma
from models.store import StoreModel
from models.item import ItemModel
from schema.item import ItemSchema


class StoreSchema(ma.ModelSchema):
    items = ma.Nested(ItemSchema, many=True)
    class Meta:
        model = StoreModel
        load_only = ("store",)
        dump_only = ("id",)
        include_fk = True
