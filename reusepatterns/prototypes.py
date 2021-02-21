import copy


class PrototypeMixin:
    # прототип

    def clone(self):
        """Clone a registered object and update inner attributes dictionary"""
        return copy.deepcopy(self)
