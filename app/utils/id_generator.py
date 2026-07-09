from pymongo import ReturnDocument
from app.db.database import counters_collection

# Starting number so IDs look like COMP-1001 instead of COMP-1
STARTING_NUMBER = 1000


def _get_next_sequence(sequence_name: str) -> int:
    """
    Atomically increments a counter stored in MongoDB and returns the new value.
    'Atomic' means: even if two people onboard a company at the EXACT same
    millisecond, MongoDB guarantees they each get a different number --
    no two companies can ever collide on the same ID.
    """
    counter = counters_collection.find_one_and_update(
        {"_id": sequence_name},
        {"$inc": {"seq": 1}},
        upsert=True,                       # create the counter if it doesn't exist yet
        return_document=ReturnDocument.AFTER,
    )
    return counter["seq"]


def generate_company_id() -> str:
    """Returns something like 'COMP-1001', 'COMP-1002', 'COMP-1003' ..."""
    number = STARTING_NUMBER + _get_next_sequence("company_id")
    return f"COMP-{number}"
