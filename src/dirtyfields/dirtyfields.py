# Adapted from http://stackoverflow.com/questions/110803/dirty-fields-in-django

from django.db.models.signals import post_save


class DirtyFieldsMixin(object):
    def __init__(self, *args, **kwargs):
        super(DirtyFieldsMixin, self).__init__(*args, **kwargs)
        post_save.connect(
            reset_state, sender=self.__class__,
            dispatch_uid='{name}-DirtyFieldsMixin-sweeper'.format(
                name=self.__class__.__name__))
        reset_state(sender=self.__class__, instance=self)

    def _as_dict(self):
        return { field.attname: getattr(self, field.attname) for field in self._meta.local_fields }

    def get_dirty_fields(self):
        new_state = self._as_dict()
        return { k: self._original_state[k] for k in self._original_state if self._original_state[k] != new_state[k] }

    def is_dirty(self):
        # in order to be dirty we need to have been saved at least once, so we
        # check for a primary key and we need our dirty fields to not be empty
        if not self.pk:
            return True
        return {} != self.get_dirty_fields()


def reset_state(sender, instance, **kwargs):
    instance._original_state = instance._as_dict()
